import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from .config import (
    PROMPT_TEMPLATE,
    SUMMARIZATION_PROMPT_TEMPLATE,
    KEYWORD_EXTRACTION_PROMPT_TEMPLATE,
)
from .logger_config import get_logger

logger = get_logger(__name__)


def generate_answer(
    language_model, user_query, context_documents, conversation_history=""
):
    """
    Generate an answer based on the user query, context documents, and conversation history.
    """
    if not user_query or not user_query.strip():
        logger.warning("generate_answer called with empty user_query.")
        # User-facing warning is handled by returning the string, which rag_deep.py will show.
        return "Your question is empty. Please type a question to get an answer."

    if (
        not context_documents
        or not isinstance(context_documents, list)
        or len(context_documents) == 0
    ):
        logger.warning("generate_answer called with no context documents.")
        return "I couldn't find relevant information in the document to answer your query. Please try rephrasing your question or ensure the document contains the relevant topics."

    logger.info(f"Generating answer for query: '{user_query[:50]}...'")
    try:
        context_text = "\n\n".join([doc.page_content for doc in context_documents])
        if not context_text.strip():
            logger.warning(
                "Context text for answer generation is empty after joining docs."
            )
            return "The relevant sections found in the document appear to be empty. Cannot generate an answer."

        logger.debug(f"Context for prompt: {context_text[:100]}...")
        conversation_prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        response_chain = conversation_prompt | language_model

        response = response_chain.invoke(
            {
                "user_query": user_query,
                "document_context": context_text,
                "conversation_history": conversation_history,
            }
        )

        if not response or not response.strip():
            logger.warning("AI model returned an empty response for answer generation.")
            st.warning(
                "The AI model returned an empty response. Please try rephrasing your question or try again later."
            )  # User feedback
            return "The AI model returned an empty response. Please try rephrasing your question or try again later."  # Also return for main script
        logger.info("Answer generated successfully.")
        return response
    except Exception as e:
        user_message = (
            "I'm sorry, but I encountered an error while trying to generate a response."
        )
        logger.exception(f"Error during answer generation: {e}")
        st.error(
            f"An error occurred while generating the answer using the AI model. Details: {e}"
        )  # Keep for user if they see it via direct call
        return f"{user_message} Please try again later or rephrase your question. (Details: {e})"


def generate_summary(language_model, full_document_text):
    """
    Generates a summary for the given document text.
    """
    if not full_document_text or not full_document_text.strip():
        logger.warning("generate_summary called with empty document text.")
        st.warning(
            "Document content is empty or contains only whitespace. Cannot generate summary."
        )
        return None
    logger.info("Generating summary...")
    try:
        summary_prompt = ChatPromptTemplate.from_template(SUMMARIZATION_PROMPT_TEMPLATE)
        summary_chain = summary_prompt | language_model
        summary = summary_chain.invoke({"document_text": full_document_text})
        if not summary or not summary.strip():
            logger.warning("AI model returned an empty summary.")
            st.warning(
                "The AI model returned an empty summary. The document might be too short or lack clear content for summarization."
            )
            return None
        logger.info("Summary generated successfully.")
        return summary
    except Exception as e:
        user_message = "Failed to generate summary due to an AI model error."
        logger.exception(f"Error during summary generation: {e}")
        st.error(
            f"An error occurred while generating the document summary using the AI model. Details: {e}"
        )
        return f"{user_message} Please try again later. (Details: {e})"


def generate_keywords(language_model, full_document_text):
    """
    Generates keywords for the given document text.
    """
    if not full_document_text or not full_document_text.strip():
        logger.warning("generate_keywords called with empty document text.")
        st.warning(
            "Document content is empty or contains only whitespace. Cannot extract keywords."
        )
        return None
    logger.info("Generating keywords...")
    try:
        keywords_prompt = ChatPromptTemplate.from_template(
            KEYWORD_EXTRACTION_PROMPT_TEMPLATE
        )
        keywords_chain = keywords_prompt | language_model
        keywords = keywords_chain.invoke({"document_text": full_document_text})
        if not keywords or not keywords.strip():
            logger.warning("AI model returned no keywords.")
            st.warning(
                "The AI model returned no keywords. The document might be too short or lack distinct terms."
            )
            return None
        logger.info("Keywords generated successfully.")
        return keywords
    except Exception as e:
        user_message = "Failed to extract keywords due to an AI model error."
        logger.exception(f"Error during keyword generation: {e}")
        st.error(
            f"An error occurred while extracting keywords using the AI model. Details: {e}"
        )
        return f"{user_message} Please try again later. (Details: {e})"
