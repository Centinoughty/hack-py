"use client";

import { ChangeEvent, KeyboardEvent, useEffect, useRef, useState } from "react";
import { BiLinkAlt, BiSend } from "react-icons/bi";
import { FaRegCopy } from "react-icons/fa";

interface ResponseProps {
  question: string;
  response: string;
}

export default function Home() {
  const [question, setQuestion] = useState<string>("");
  const [questions, setQuestions] = useState<ResponseProps[]>([]);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    if (questions.length > 0) {
      window.scrollTo({
        top: document.documentElement.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [questions]);

  async function handleSubmit() {
    if (question.trim() === "") {
      return;
    }

    let askedQuestion = question;
    let response;
    try {
      response = await fetch("https://api.openai.com/v1/chat/completions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${process.env.NEXT_PUBLIC_OPENAI_KEY}`,
        },
        body: JSON.stringify({
          model: "gpt-3.5-turbo",
          messages: [
            { role: "system", content: "You are a helpful assistant" },
            { role: "user", content: askedQuestion },
          ],
          max_tokens: 150,
          temperature: 0.7,
        }),
      });

      const data = await response?.json();
      console.log(data);
      setQuestions([
        ...questions,
        {
          question: question.trim(),
          response: "data.choices[0].message.content",
        },
      ]);
    } catch (error) {
      console.log(error);
    }

    setQuestion("");
  }

  function handleKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === "Enter") {
      event.preventDefault();
      handleSubmit();
    }
  }

  function handleButtonClick() {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  }

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (file) {
      console.log("File selected:", file.name);
    }
  }

  return (
    <>
      <main className="relative min-h-screen font-mono">
        <div className="fixed top-2 left-2 text-white tracking-widest text-xl">
          AGGIN APP
        </div>
        <ul
          className={`${
            questions.length && "pt-4 pb-28"
          } mx-auto flex flex-col items-center w-[600px] gap-8`}
        >
          {questions.length ? (
            questions.map((question, idx) => (
              <div
                key={idx}
                className="text-white flex flex-col items-start gap-2 w-full group"
              >
                <p className="ml-auto px-4 py-3 text-left break-words rounded-3xl bg-white/15 max-w-[300px]">
                  {question.question}
                </p>
                <p className="text-left rounded-3xl rounded-tr-none p-4">
                  {question.response}
                </p>
                <button>
                  <FaRegCopy
                    size={18}
                    className="absolute hidden duration-300 transition-all group-hover:block text-white/60 -translate-y-3"
                  />
                </button>
              </div>
            ))
          ) : (
            <div className="h-screen flex justify-center items-center text-white text-3xl">
              Ask anything!!
            </div>
          )}
        </ul>
        <div className="p-2 fixed bottom-10 left-1/2 transform -translate-x-1/2 w-[400px] md:w-[500px] lg:w-[600px] rounded-full flex items-center gap-2 border-2 border-gray-500 bg-black/50 backdrop-blur-md">
          <button className="ml-2" onClick={handleButtonClick}>
            <BiLinkAlt size={30} color="white" />
          </button>
          <input
            ref={fileInputRef}
            type="file"
            className="hidden"
            onChange={handleFileChange}
          />
          <input
            className="flex-grow bg-transparent outline-none text-white px-4 py-2 text-lg font-mono tracking-wider placeholder:text-white/45 placeholder:font-mono placeholder:tracking-wide"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Enter your question"
            type="text"
          />
          <button className="mr-2" onClick={handleSubmit}>
            <BiSend size={35} color="white" />
          </button>
        </div>
      </main>
    </>
  );
}
