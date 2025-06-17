import React, { useState, useEffect } from 'react';
import { initializeApp, FirebaseApp } from 'firebase/app'; // Import FirebaseApp type
import { getAuth, signInAnonymously, signInWithCustomToken, onAuthStateChanged, Auth } from 'firebase/auth'; // Import Auth type
import { getFirestore, Firestore, collection, addDoc } from 'firebase/firestore'; // Import Firestore functions

// Define a type for the quote object
interface Quote {
  text: string;
  author: string;
}

function App() {
  // State variables for Firebase instances and user information
  const [db, setDb] = useState<Firestore | null>(null); // Explicitly type db as Firestore or null
  const [auth, setAuth] = useState<Auth | null>(null);   // Explicitly type auth as Auth or null
  const [userId, setUserId] = useState<string | null>(null);
  const [isAuthReady, setIsAuthReady] = useState<boolean>(false);
  const [loadingFirebase, setLoadingFirebase] = useState<boolean>(true);

  // State variables for quote generation
  const [currentQuote, setCurrentQuote] = useState<Quote>({ text: "Click 'Generate New Quote' to get inspired!", author: "Welcome" });
  const [isGeneratingQuote, setIsGeneratingQuote] = useState<boolean>(false);
  const [quoteError, setQuoteError] = useState<string | null>(null);

  // State variables for saving quotes
  const [isSavingQuote, setIsSavingQuote] = useState<boolean>(false);
  const [saveMessage, setSaveMessage] = useState<string | null>(null); // For success/error messages

  useEffect(() => {
    // This effect runs once when the component mounts to initialize Firebase and set up auth.
    const initializeFirebase = async () => {
      try {
        // Retrieve Firebase config and app ID from the global Canvas environment variables
        // Ensure firebaseConfig is typed correctly
        const firebaseConfig: { [key: string]: any } = typeof __firebase_config !== 'undefined' ? JSON.parse(__firebase_config) : {};
        const appId: string = typeof __app_id !== 'undefined' ? __app_id : 'default-quote-app-id';

        // Initialize Firebase app
        const app: FirebaseApp = initializeApp(firebaseConfig);
        const firestoreDb: Firestore = getFirestore(app);
        const firebaseAuth: Auth = getAuth(app);

        setDb(firestoreDb);
        setAuth(firebaseAuth);

        // Set up authentication state listener
        const unsubscribe = onAuthStateChanged(firebaseAuth, async (user) => {
          if (user) {
            // User is signed in
            setUserId(user.uid);
            setIsAuthReady(true);
          } else {
            // User is signed out or not authenticated yet
            const initialAuthToken: string | null = typeof __initial_auth_token !== 'undefined' ? __initial_auth_token : null;
            if (initialAuthToken) {
              try {
                await signInWithCustomToken(firebaseAuth, initialAuthToken);
              } catch (error) {
                console.error("Error signing in with custom token:", error);
                await signInAnonymously(firebaseAuth);
              }
            } else {
              await signInAnonymously(firebaseAuth);
            }
          }
          setLoadingFirebase(false);
        });

        return () => unsubscribe();
      } catch (error) {
        console.error("Failed to initialize Firebase:", error);
        setLoadingFirebase(false);
      }
    };

    initializeFirebase();
  }, []);

  // Function to fetch a new quote from the Gemini API
  const generateNewQuote = async () => {
    setIsGeneratingQuote(true);
    setQuoteError(null);
    setSaveMessage(null); // Clear save message on new quote generation
    try {
      const prompt: string = "Generate a short, inspiring quote (max 20 words) with an author. Format as 'Quote: \"[The quote]\" Author: [The author]'";
      let chatHistory: Array<{ role: string; parts: Array<{ text: string }> }> = [];
      chatHistory.push({ role: "user", parts: [{ text: prompt }] });
      const payload = { contents: chatHistory };
      const apiKey: string = ""; // Canvas will provide this dynamically

      const apiUrl: string = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`;

      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const result = await response.json();
      console.log("Gemini API Response:", result);

      if (result.candidates && result.candidates.length > 0 &&
          result.candidates[0].content && result.candidates[0].content.parts &&
          result.candidates[0].content.parts.length > 0) {
        const text: string = result.candidates[0].content.parts[0].text;
        const quoteMatch = text.match(/Quote: "([^"]+)"/);
        const authorMatch = text.match(/Author: (.+)/);

        const extractedQuote: string = quoteMatch ? quoteMatch[1] : text.split("Author:")[0].replace("Quote:", "").trim();
        const extractedAuthor: string = authorMatch ? authorMatch[1].trim() : "Unknown";

        setCurrentQuote({ text: extractedQuote, author: extractedAuthor });
      } else {
        setQuoteError("Failed to generate quote. Please try again.");
        setCurrentQuote({ text: "Error: Could not generate quote.", author: "" });
        console.error("Gemini API response structure unexpected:", result);
      }
    } catch (error: any) {
      console.error("Error generating quote:", error);
      setQuoteError(`An error occurred: ${error.message || 'Unknown error'}`);
      setCurrentQuote({ text: "Error: An unexpected error occurred.", author: "" });
    } finally {
      setIsGeneratingQuote(false);
    }
  };

  // Function to save the current quote to Firestore
  const saveQuote = async () => {
    if (!db || !userId || !isAuthReady) {
      setSaveMessage("Firebase not ready or user not authenticated.");
      return;
    }

    if (!currentQuote.text || currentQuote.text === "Click 'Generate New Quote' to get inspired!") {
      setSaveMessage("Please generate a quote before saving.");
      return;
    }

    setIsSavingQuote(true);
    setSaveMessage(null);
    try {
      const appId: string = typeof __app_id !== 'undefined' ? __app_id : 'default-quote-app-id';
      const quotesCollectionRef = collection(db, `artifacts/${appId}/users/${userId}/quotes`);
      await addDoc(quotesCollectionRef, {
        text: currentQuote.text,
        author: currentQuote.author,
        createdAt: new Date().toISOString(), // Store creation timestamp
      });
      setSaveMessage("Quote saved successfully!");
    } catch (error: any) {
      console.error("Error saving quote:", error);
      setSaveMessage(`Error saving quote: ${error.message || 'Unknown error'}`);
    } finally {
      setIsSavingQuote(false);
      // Clear message after a few seconds
      setTimeout(() => setSaveMessage(null), 3000);
    }
  };


  if (loadingFirebase) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-100">
        <div className="text-xl text-gray-700">Loading app...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-500 to-indigo-600 flex flex-col items-center justify-center p-4">
      {/* Main Container for the Quote App */}
      <div className="bg-white p-8 rounded-2xl shadow-xl max-w-lg w-full text-center transform transition-all duration-300 hover:scale-105">
        <h1 className="text-4xl font-extrabold text-gray-800 mb-6 tracking-tight">
          Inspire Quotes
        </h1>

        {/* User ID Display */}
        {userId && (
          <p className="text-sm text-gray-500 mb-6 bg-gray-100 p-2 rounded-lg break-all">
            Your User ID: <span className="font-semibold text-gray-700">{userId}</span>
          </p>
        )}

        {/* Quote Display Area */}
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-6 mb-8 min-h-[120px] flex flex-col items-center justify-center relative">
          {isGeneratingQuote ? (
            <div className="text-center text-gray-600">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-600 mx-auto mb-2"></div>
              <p>Generating inspiration...</p>
            </div>
          ) : (
            <>
              <p className="text-xl italic text-gray-700 mb-2">
                "{currentQuote.text}"
              </p>
              <p className="text-lg font-semibold text-gray-600">- {currentQuote.author}</p>
            </>
          )}
          {quoteError && (
            <p className="text-red-500 text-sm mt-2">{quoteError}</p>
          )}
        </div>

        {/* Save Message Display */}
        {saveMessage && (
          <p className={`text-sm mb-4 ${saveMessage.startsWith("Error") ? 'text-red-600' : 'text-green-600'}`}>
            {saveMessage}
          </p>
        )}

        {/* Buttons */}
        <div className="space-y-4">
          <button
            onClick={generateNewQuote}
            disabled={isGeneratingQuote || isSavingQuote} // Disable if saving too
            className={`w-full bg-indigo-700 hover:bg-indigo-800 text-white font-bold py-3 px-6 rounded-xl shadow-lg transition-all duration-200 ease-in-out transform ${isGeneratingQuote || isSavingQuote ? 'opacity-50 cursor-not-allowed' : 'hover:-translate-y-1 hover:shadow-xl'} focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-opacity-75`}
          >
            {isGeneratingQuote ? 'Generating...' : 'Generate New Quote'}
          </button>
          <button
            onClick={saveQuote}
            disabled={!currentQuote.text || currentQuote.text === "Click 'Generate New Quote' to get inspired!" || isGeneratingQuote || isSavingQuote}
            className={`w-full bg-purple-700 hover:bg-purple-800 text-white font-bold py-3 px-6 rounded-xl shadow-lg transition-all duration-200 ease-in-out transform ${(!currentQuote.text || currentQuote.text === "Click 'Generate New Quote' to get inspired!" || isGeneratingQuote || isSavingQuote) ? 'opacity-50 cursor-not-allowed' : 'hover:-translate-y-1 hover:shadow-xl'} focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-opacity-75`}
          >
            {isSavingQuote ? 'Saving...' : 'Save Quote'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
