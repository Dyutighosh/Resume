#!/usr/bin/env python3
"""Check local href/src references in the static website."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


SITE_ROOT = Path(__file__).resolve().parent.parent
HTML_FILES = sorted(SITE_ROOT.glob("*.html"))


class ReferenceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: list[tuple[str, str]] = []
        self.counts = {"title": 0, "h1": 0, "main": 0}
        self.ids: list[str] = []
        self.images_without_alt = 0
        self.current_navigation_items = 0
        self.publication_statuses: list[str] = []
        self.heading_levels: list[int] = []
        self.paper_disclosures = 0
        self.summaries = 0
        self.research_paper_rows = 0
        self.text_chunks: list[str] = []
        self.ignored_text_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag in {"script", "style"}:
            self.ignored_text_depth += 1
        if tag in self.counts:
            self.counts[tag] += 1
        if len(tag) == 2 and tag.startswith("h") and tag[1].isdigit():
            self.heading_levels.append(int(tag[1]))
        if attributes.get("id"):
            self.ids.append(attributes["id"] or "")
        if tag == "img" and "alt" not in attributes:
            self.images_without_alt += 1
        if attributes.get("aria-current") == "page":
            self.current_navigation_items += 1
        classes = (attributes.get("class") or "").split()
        if "publication-item" in classes:
            self.publication_statuses.append(attributes.get("data-status") or "missing")
        if tag == "details" and "paper-disclosure" in classes:
            self.paper_disclosures += 1
        if "research-paper-row" in classes:
            self.research_paper_rows += 1
        if tag == "summary":
            self.summaries += 1
        for name in ("href", "src"):
            value = attributes.get(name)
            if value:
                self.references.append((name, value))

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self.ignored_text_depth:
            self.ignored_text_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self.ignored_text_depth:
            self.text_chunks.append(data)


def resolve_reference(source: Path, reference: str) -> Path | None:
    parsed = urlsplit(reference)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None
    candidate = unquote(parsed.path)
    if candidate.startswith("/"):
        return SITE_ROOT / candidate.lstrip("/")
    return source.parent / candidate


def main() -> int:
    errors: list[str] = []
    checked = 0
    raw_email_addresses = (
        ".".join(("soumyadyuti", "ghosh")) + "@" + ".".join(("gmail", "com")),
        "".join(("sg", "8466")) + "@" + ".".join(("nyu", "edu")),
    )

    for html_file in HTML_FILES:
        html_text = html_file.read_text(encoding="utf-8")
        parser = ReferenceParser()
        parser.feed(html_text)

        for forbidden_text in (
            "My primary research focus is on privacy-preserving computation",
            "Peer-reviewed journal articles and conference papers addressing",
            "Selected activities in research, teaching, peer review",
            "Professional engineering experience, research appointments and internships",
            "Selected technical capabilities from my research and engineering work",
            "For research discussions, academic collaboration, invited talks",
            "Selected engineering tools and experimental platforms",
            "Information Security Education and Awareness initiative",
            "Centre on Hardware Entrepreneurship Research &amp; Development",
            "Software and Side Projects",
            "Privacy and cryptography toolchain",
            "Appointments &amp; Experience",
            "Reviewer and external reviewer",
            "receiver-authorized",
            "Privacy-Aware Smart-Grid Control",
            "Privacy-aware real-time pricing",
            "real-time electricity pricing",
            "Email Composer",
            "data-mail-composer",
            "data-mail-panel",
            "<dt>Languages</dt>",
            "Email NYUAD",
            "Email Gmail",
            "data-email-actions",
            "data-email-target",
            "PyTorch and TensorFlow",
            "Secure two-party and multi-party computation",
            "Matplotlib, and tqdm",
            "Hugging Face Datasets",
            "WHU-Hi-HongHu",
            "CIFAR-10",
            "Pillow",
            "tifffile",
            "I captained departmental football teams",
            "Research Scholar Football Championship",
        ):
            if forbidden_text in html_text:
                errors.append(f"{html_file.name}: found removed text {forbidden_text}")

        if 'class="cv-link"' in html_text:
            errors.append(f"{html_file.name}: CV must not appear in the top navigation")
        if "mailto:" in html_text or any(
            address in html_text for address in raw_email_addresses
        ):
            errors.append(f"{html_file.name}: found a non-obfuscated email address")
        if html_file.name == "index.html" and any(
            address not in html_text
            for address in (
                "sg8466 [at] nyu [dot] edu",
                "soumyadyuti [dot] ghosh [at] gmail [dot] com",
            )
        ):
            errors.append(f"{html_file.name}: missing an obfuscated contact address")
        if html_file.name != "404.html":
            for required_markup in (
                'href="contact.html"',
                'href="hobbies.html"',
                'href="experience.html"',
                "Skills &amp; Hobbies",
                'src="assets/site.js"',
            ):
                if required_markup not in html_text:
                    errors.append(
                        f"{html_file.name}: missing shared navigation or script markup "
                        f"{required_markup}"
                    )
        if html_file.name == "contact.html":
            for required_contact_text in (
                "Modern Microprocessors Architecture Lab",
                "P.O. Box 129188",
                "sg8466 [at] nyu [dot] edu",
                "soumyadyuti [dot] ghosh [at] gmail [dot] com",
            ):
                if required_contact_text not in html_text:
                    errors.append(
                        f"{html_file.name}: missing required contact detail "
                        f"{required_contact_text}"
                    )
        if html_file.name == "hobbies.html":
            if ";" in "".join(parser.text_chunks):
                errors.append(
                    f"{html_file.name}: use bullet points instead of semicolon-separated text"
                )
            for required_profile_text in (
                "OpenFHE",
                "Secure multi-party computation",
                "BFV and CKKS",
                "Python and PyTorch",
                "scikit-learn, etc.",
                "dominant-pole analysis in the z-plane",
                "Sports",
                "Manchester United",
                "Bridge",
                "rapid rating of 2267",
                "Correlation Power Analysis",
                "Differential Fault Analysis",
            ):
                if required_profile_text not in html_text:
                    errors.append(
                        f"{html_file.name}: missing CV-derived skills or hobbies detail "
                        f"{required_profile_text}"
                    )
        if html_file.name == "experience.html":
            for required_experience_text in (
                "Work Experience",
                "Research &amp; Internship Experience",
                "Selected Research Projects &amp; Tools",
                "Wipro Digital",
                "Visiting Research Scholar",
                "KAVACH: Key Analysis and Vulnerability Assessment",
            ):
                if required_experience_text not in html_text:
                    errors.append(
                        f"{html_file.name}: missing CV-derived experience or project detail "
                        f"{required_experience_text}"
                    )
            if parser.paper_disclosures != 8 or parser.summaries != 8:
                errors.append(
                    f"{html_file.name}: expected 8 expandable experience and project "
                    f"entries, found {parser.paper_disclosures} disclosures and "
                    f"{parser.summaries} summaries"
                )

        for element, count in parser.counts.items():
            if count != 1:
                errors.append(f"{html_file.name}: expected one <{element}>, found {count}")
        duplicate_ids = sorted({item for item in parser.ids if parser.ids.count(item) > 1})
        if duplicate_ids:
            errors.append(f"{html_file.name}: duplicate IDs {duplicate_ids}")
        if parser.images_without_alt:
            errors.append(f"{html_file.name}: {parser.images_without_alt} image(s) without alt text")
        if html_file.name != "404.html" and parser.current_navigation_items != 1:
            errors.append(
                f"{html_file.name}: expected one current navigation item, "
                f"found {parser.current_navigation_items}"
            )
        for previous, current in zip(parser.heading_levels, parser.heading_levels[1:]):
            if current > previous + 1:
                errors.append(
                    f"{html_file.name}: heading level jumps from h{previous} to h{current}"
                )
        if html_file.name == "publications.html":
            expected = {"accepted": 3, "published": 6}
            actual = {status: parser.publication_statuses.count(status) for status in expected}
            if actual != expected or len(parser.publication_statuses) != 9:
                errors.append(f"{html_file.name}: unexpected publication counts {actual}")
        if html_file.name == "index.html":
            if '<h2 class="column-heading">Experiences</h2>' not in html_text:
                errors.append(f"{html_file.name}: missing Experiences column heading")
            if parser.paper_disclosures != 0 or parser.summaries != 0:
                errors.append(
                    f"{html_file.name}: expected no current-research accordions, found "
                    f"{parser.paper_disclosures} disclosures and {parser.summaries} summaries"
                )
        if html_file.name == "research.html":
            if (
                parser.paper_disclosures != 6
                or parser.summaries != 6
                or parser.research_paper_rows != 9
            ):
                errors.append(
                    f"{html_file.name}: expected 9 static papers, 3 ongoing-work "
                    "accordions, and 3 side-project accordions; found "
                    f"{parser.research_paper_rows} static papers, "
                    f"{parser.paper_disclosures} disclosures, and {parser.summaries} summaries"
                )
            for required_research_text in (
                "Privacy-preserving computation and systems security",
                "Side Projects",
                "Hardware-in-the-loop smart-grid testbed at IIT-KGP",
                "Secure smart meter prototype",
                "PLC security assessment",
                "Privacy-Aware Cyber-Physical Control Systems",
                "Privacy-aware cyber-physical control under intentionally skipped executions",
                "HARVEY paper at NDSS 2017",
            ):
                if required_research_text not in html_text:
                    errors.append(
                        f"{html_file.name}: missing requested research content "
                        f"{required_research_text}"
                    )

        for attribute, reference in parser.references:
            target = resolve_reference(html_file, reference)
            if target is None:
                continue
            checked += 1
            if not target.exists():
                errors.append(f"{html_file.name}: missing {attribute}=\"{reference}\"")

    site_script = (SITE_ROOT / "assets" / "site.js").read_text(encoding="utf-8")
    analytics_script = SITE_ROOT / "assets" / "analytics.js"
    if "assets/analytics.js" not in site_script or not analytics_script.exists():
        errors.append("assets/site.js: missing the configurable analytics loader")
    for removed_email_control_code in (
        "data-mail-composer",
        "data-mail-panel",
        "contact-compose",
        "data-email-target",
        "data-email-actions",
        "openEmailDraft",
    ):
        if removed_email_control_code in site_script:
            errors.append(
                f"assets/site.js: found removed email-control code "
                f"{removed_email_control_code}"
            )

    if errors:
        print("Site check failed:")
        for item in errors:
            print(f"- {item}")
        return 1

    print(
        f"OK: checked structure and {checked} local references across "
        f"{len(HTML_FILES)} HTML files; publication counts are 3 newly accepted "
        "and 6 published papers, with 9 static research papers, 3 ongoing-work "
        "accordions, 3 side-project accordions, and 8 expandable experience or "
        "project entries; the Contact page retains obfuscated email contacts "
        "without email shortcut controls."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
