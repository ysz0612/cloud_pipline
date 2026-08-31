import React from "react";
import ReactDOM from "react-dom/client";
import {
    QueryClient,
    QueryClientProvider,
} from "@tanstack/react-query";
import { createGlobalStyle } from "styled-components";

import App from "./App";

const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            retry: 1,
            refetchOnWindowFocus: false,
        },
        mutations: {
            retry: 0,
        },
    },
});

const GlobalStyle = createGlobalStyle`
  * {
    box-sizing: border-box;
  }

  html {
    font-family:
      Pretendard,
      "Noto Sans KR",
      Arial,
      sans-serif;
  }

  body {
    margin: 0;
    min-width: 320px;
    color: #22283b;
    background: #f5f6fa;
  }

  button,
  input {
    font: inherit;
  }
`;

ReactDOM.createRoot(
    document.getElementById("root"),
).render(
    <React.StrictMode>
        <QueryClientProvider client={queryClient}>
            <GlobalStyle />
            <App />
        </QueryClientProvider>
    </React.StrictMode>,
);