(defmacro with-baseurl [#* items]
  `(do
     (if (.endswith base_url "/")
         (Combine base_url #*~items)
         (Combine base_url "/" #*~items))))
