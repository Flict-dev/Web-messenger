import React, { useState, useEffect } from "react";

const FormError: React.FC<{ error: string }> = ({ error }) => {
  return (
    <div className="form_error">
      <p className="form_error_msg">{error}</p>
    </div>
  );
};

export { FormError };
