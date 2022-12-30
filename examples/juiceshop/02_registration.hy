;; Get the first question
(setv get_security_question
      (Flow
        (Request.get (with-baseurl "api/SecurityQuestions/"))
        ;; Extract outputs below from the response
        :outputs [question]
        ;; Print those outputs on the command line
        :operations [(Print question)
                     (Next "register_user")]))

;; Register new user
(setv register_user
      (Flow
        (Request.post (with-baseurl "api/Users/")
          :json
          {"email" email
           "password" password
           "passwordRepeat" password
           "securityQuestion" question
           "securityAnswer" answer})
        :outputs [user_id]
        :operations [(Grep
                       :regex "email must be unique"
                       ;; This message is returned when reusing the email
                       :action [(Failure "Email already registered, use a new email")])
                     (Print.body)
                     (Next "security_answer")]))

;; Submit security answer
(setv security_answer
      (Flow
        (Request.post
          (with-baseurl "api/SecurityAnswers/")
          :json
          {"UserId" user_id
           "answer" answer
           "SecurityQuestionId" 1})
        :operations
        [(Http
           :status 201
           :action [(Success "User created successfully")]
           :otherwise (Failure "Couldn't create user"))]))


(setv register
      (FlowGraph get_security_question))
