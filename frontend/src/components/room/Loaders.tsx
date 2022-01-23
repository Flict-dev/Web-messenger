import ReactLoading from "react-loading";
import React from "react";
import "./../../style/Loader.css";

const CssLoader: React.FC<{ message: string; showE: boolean }> = ({
  message,
  showE,
}) => {
  return (
    <div className="loader_wrapper">
      {showE ? <h1 className="load_err_t">Error</h1> : <div id="loader"></div>}
      <p className="loader_text">{message}</p>
    </div>
  );
};
export default CssLoader;
