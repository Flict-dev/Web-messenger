import React, { useState, useEffect } from "react";

type Props = {
  show: boolean;
  error: string;
};

const FormErrorData: React.FC<{ error: string }> = ({ error }) => {
  return (
    <div className="form_error">
      <p className="form_error_msg">{error}</p>
    </div>
  );
};

const FormError: React.FC<{ data: Props }> = ({ data }) => {

  const [showError, setError] = useState<Boolean>(data.show);
  
  if (data.show) {
    setTimeout((): void => {
      setError(false);
    }, 9000);
  }

  return (
    <div className="form_errors">
      {showError && <FormErrorData error={data.error} />}
    </div>
  );
};

export { FormError };
