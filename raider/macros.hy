(defmacro with-baseurl [#* items]
  `(do
     (if (or
           (.endswith base_url "/")
           (.startswith (get ~items 0) "/"))
         (Combine base_url #*~items)
         (Combine base_url "/" #*~items))))

(defmacro add_pkce_challenge []
  (import pkce)
  (global code_verifier)
  (global code_challenge)
  
  (setv code_verifier (.generate_code_verifier pkce :length 43))
  (setv code_challenge (.get_code_challenge pkce code_verifier))
  `(do
     (if pkce_enabled
         {"code_challenge" ~code_challenge
          "code_challenge_method" "S256"}
         {})))

(defmacro add_pkce_verifier []
  `(do
     (if pkce_enabled
         {"code_verifier" ~code_verifier}
         {})))

