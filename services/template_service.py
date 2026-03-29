from __future__ import annotations
from models.template import Template
from storage.repositories.templates_repo import TemplatesRepository

class TemplateService:
    def __init__(self, repo: TemplatesRepository) -> None:
        self.repo = repo

    def list_templates(self) -> list[Template]:
        return self.repo.all()

    def save_template(self, template: Template) -> Template:
        return self.repo.save(template)

    def delete_template(self, template_id: int) -> None:
        self.repo.delete(template_id)

    def find_by_name(self, name: str) -> Template | None:
        return self.repo.get_by_name(name)
