from typing import Annotated

from semantic_kernel.functions import kernel_function

from rag.retriever import search_knowledge


class KnowledgeTools:

    @kernel_function(
        name="search_insurance_knowledge",
        description=(
            "Search insurance underwriting, coverage, and fraud "
            "knowledge and return relevant evidence."
        ),
    )
    def search_insurance_knowledge(
        self,
        query: Annotated[
            str,
            "The insurance question or rule to search for."
        ],
    ) -> Annotated[
        str,
        "Relevant insurance knowledge and evidence."
    ]:

        results = search_knowledge(
            query=query,
            top_k=3,
            hybrid=True,
        )

        if not results:
            return "No relevant insurance knowledge was found."

        evidence = []

        for result in results:
            evidence.append(
                f"""
Source: {result.source}
Category: {result.category}
Score: {result.score}

Content:
{result.content}
"""
            )

        return "\n---\n".join(evidence)