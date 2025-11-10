"""Prompt builder service for generating structured prompts from templates."""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

from jinja2 import Template, TemplateNotFound

from backend.app.models.database import CompanyProfile

logger = logging.getLogger(__name__)


class PromptBuilder:
    """Build structured prompts from templates with company context."""

    def __init__(self):
        """Initialize prompt builder with templates directory."""
        self.prompts_dir = Path("backend/app/prompts")
        if not self.prompts_dir.exists():
            logger.warning(f"Prompts directory not found: {self.prompts_dir}")
            self.prompts_dir.mkdir(parents=True, exist_ok=True)

    def build_prompt(
        self,
        doc_type: str,
        data: Dict[str, Any],
        company_profile: Optional[CompanyProfile] = None
    ) -> str:
        """
        Build prompt from template and data.

        Args:
            doc_type: Type of document (e.g., 'job_description', 'offer_letter')
            data: Dictionary with template variables
            company_profile: Optional company profile for branding context

        Returns:
            str: Rendered prompt ready for AI generation

        Raises:
            ValueError: If template file not found
        """
        template_path = self.prompts_dir / f"{doc_type}.txt"

        if not template_path.exists():
            raise ValueError(
                f"Prompt template not found: {doc_type}. "
                f"Expected at: {template_path}"
            )

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()

            template = Template(template_content)

            # Merge company data if available
            context = {**data}

            if company_profile:
                context.update({
                    "company_name": company_profile.name or "Our Company",
                    "industry": company_profile.industry or "Technology",
                    "company_size": company_profile.size or "Growing team",
                    "company_location": company_profile.location or "",
                    "company_website": company_profile.website or "",
                    "company_description": company_profile.description or "",
                    "company_values": company_profile.values or ""
                })

                logger.info(
                    f"Building prompt with company context: {company_profile.name}",
                    extra={"doc_type": doc_type, "company_id": company_profile.id}
                )
            else:
                # Provide defaults if no company profile
                context.setdefault("company_name", "Our Company")
                context.setdefault("industry", "Technology")
                context.setdefault("company_size", "Growing team")

                logger.info(
                    f"Building prompt without company context",
                    extra={"doc_type": doc_type}
                )

            # Render prompt
            prompt = template.render(**context)

            logger.debug(
                f"Prompt built successfully",
                extra={
                    "doc_type": doc_type,
                    "prompt_length": len(prompt),
                    "has_company": company_profile is not None
                }
            )

            return prompt

        except TemplateNotFound as e:
            raise ValueError(f"Template rendering failed: {e}")
        except Exception as e:
            logger.error(
                f"Error building prompt for {doc_type}: {e}",
                exc_info=True
            )
            raise


__all__ = ["PromptBuilder"]
