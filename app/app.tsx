import { StrictMode } from "react";
import Index from "./index";
import BookProvider from "@/context/BookContext";

const App = () => {
    return(
        <StrictMode>
            <BookProvider>
                <Index />
            </BookProvider>
        </StrictMode>
    );
}

export default App;