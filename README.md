# Multi-Chatbot-Orchestration-Framework
A framework where multiple chatbots of differing specialties can work together to answer any intent accurately to a user

Bot Orchestrator-What?:
‘Bot Orchestrator’ Scope
Exposes a protocol for sending a message/receiving to end user
Modular. Can easily change to use any messaging platform desired
Provides bot-agnostic abstraction layer (Bot A does not need to know Bot B)
Maintains conversation context data (incl. the current responding bot)
Holds logic for choice of correct chatbot to respond for the best intent found

Bot Orchestrator-How?:
Bot Orchestrator Implementation
SaaS serverless technology (currently AWS Lambda/API Gateway)
Use of customized NLP engines to determine the best course of action
Ability to connect with many different messaging platforms due to modular design
Proof of concept
Testing with Lex chatbots (Amazon)
Testing with Dialogflow chatbots (Google)


