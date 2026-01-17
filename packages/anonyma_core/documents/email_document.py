"""
Email document handler (.eml and .msg formats).

Handles email messages with:
- Header extraction (From, To, CC, Subject, Date)
- Body text extraction (plain text and HTML)
- Attachment handling
- Email reconstruction
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import email
from email import policy
from email.parser import BytesParser
import io

from .base import BaseDocument, DocumentFormat, DocumentMetadata
from ..logging_config import get_logger
from ..exceptions import DocumentProcessingError

logger = get_logger(__name__)


class EmailDocument(BaseDocument):
    """
    Email document handler for .eml and .msg files.

    Supports:
    - .eml format (standard RFC 822)
    - Header extraction (From, To, CC, BCC, Subject)
    - Body extraction (plain text and HTML)
    - Attachment detection
    - Email reconstruction with anonymized content

    Note: For .msg files, requires extract-msg library.
    """

    def __init__(self, file_path: Path):
        """
        Initialize email document handler.

        Args:
            file_path: Path to email file

        Raises:
            DocumentProcessingError: If email can't be loaded
        """
        self._message = None
        self._headers = {}
        self._body_plain = ""
        self._body_html = ""

        super().__init__(file_path)

        # Load document
        self._load_document()

    def _load_document(self):
        """Load email document"""
        if self.file_path.suffix.lower() == ".eml":
            self._load_eml()
        elif self.file_path.suffix.lower() == ".msg":
            self._load_msg()
        else:
            raise DocumentProcessingError(
                f"Unsupported email format: {self.file_path.suffix}",
                {"supported": [".eml", ".msg"]}
            )

    def _load_eml(self):
        """Load .eml file (standard email format)"""
        try:
            with open(self.file_path, 'rb') as f:
                self._message = BytesParser(policy=policy.default).parse(f)

            logger.info(
                f"EML file loaded successfully",
                extra={
                    "extra_fields": {
                        "subject": self._message.get('subject', 'N/A'),
                        "file_size": self.get_file_size(),
                    }
                },
            )

        except Exception as e:
            logger.error(f"Failed to load EML file: {e}", exc_info=True)
            raise DocumentProcessingError(
                f"Failed to load EML file: {str(e)}",
                {"file_path": str(self.file_path)}
            )

    def _load_msg(self):
        """Load .msg file (Outlook format)"""
        try:
            import extract_msg

            msg = extract_msg.Message(self.file_path)

            # Convert to standard email message structure
            self._message = msg
            self._headers = {
                'from': msg.sender,
                'to': msg.to,
                'cc': msg.cc,
                'subject': msg.subject,
                'date': msg.date,
            }
            self._body_plain = msg.body

            logger.info(
                f"MSG file loaded successfully",
                extra={
                    "extra_fields": {
                        "subject": msg.subject,
                        "file_size": self.get_file_size(),
                    }
                },
            )

        except ImportError:
            raise DocumentProcessingError(
                "extract-msg not installed. Install with: pip install extract-msg",
                {"required_package": "extract-msg"},
            )
        except Exception as e:
            logger.error(f"Failed to load MSG file: {e}", exc_info=True)
            raise DocumentProcessingError(
                f"Failed to load MSG file: {str(e)}",
                {"file_path": str(self.file_path)}
            )

    def _detect_format(self) -> DocumentFormat:
        """Detect format (always EMAIL for this handler)"""
        return DocumentFormat.EMAIL

    def _extract_metadata(self) -> DocumentMetadata:
        """Extract email metadata"""
        file_stats = self.file_path.stat()

        # Extract email headers
        if isinstance(self._message, email.message.EmailMessage):
            subject = self._message.get('subject', 'No Subject')
            from_addr = self._message.get('from', 'Unknown')
            date_str = self._message.get('date')

            # Parse date
            email_date = None
            if date_str:
                try:
                    from email.utils import parsedate_to_datetime
                    email_date = parsedate_to_datetime(date_str)
                except Exception as e:
                    logger.debug(f"Failed to parse email date: {e}")

        else:  # MSG file
            subject = self._headers.get('subject', 'No Subject')
            from_addr = self._headers.get('from', 'Unknown')
            email_date = self._headers.get('date')

        return DocumentMetadata(
            file_name=self.file_path.name,
            file_size=file_stats.st_size,
            format=DocumentFormat.EMAIL,
            title=subject,
            author=from_addr,
            creation_date=email_date,
            is_scanned=False,
            custom={
                "subject": subject,
                "from": from_addr,
                "has_attachments": self._has_attachments(),
            }
        )

    def _has_attachments(self) -> bool:
        """Check if email has attachments"""
        if isinstance(self._message, email.message.EmailMessage):
            return any(part.get_content_disposition() == 'attachment'
                      for part in self._message.iter_parts())
        return False

    def extract_text(self) -> str:
        """
        Extract all text from email.

        Extracts:
        - Headers (From, To, Subject, Date)
        - Plain text body
        - HTML body (converted to text)
        - Attachment names

        Returns:
            Extracted text content

        Raises:
            DocumentProcessingError: If extraction fails
        """
        try:
            text_parts = []

            # Extract headers
            if isinstance(self._message, email.message.EmailMessage):
                text_parts.append("[Email Headers]")
                text_parts.append(f"From: {self._message.get('from', 'N/A')}")
                text_parts.append(f"To: {self._message.get('to', 'N/A')}")

                cc = self._message.get('cc')
                if cc:
                    text_parts.append(f"CC: {cc}")

                text_parts.append(f"Subject: {self._message.get('subject', 'N/A')}")
                text_parts.append(f"Date: {self._message.get('date', 'N/A')}")
                text_parts.append("")

                # Extract body
                text_parts.append("[Email Body]")

                # Get plain text body
                body_text = ""
                for part in self._message.walk():
                    content_type = part.get_content_type()

                    if content_type == 'text/plain':
                        try:
                            body_text = part.get_content()
                            break
                        except Exception as e:
                            logger.debug(f"Failed to extract plain text: {e}")

                    elif content_type == 'text/html' and not body_text:
                        # Fallback to HTML if no plain text
                        try:
                            html_content = part.get_content()
                            # Simple HTML to text conversion
                            import re
                            body_text = re.sub('<[^<]+?>', '', html_content)
                        except Exception as e:
                            logger.debug(f"Failed to extract HTML: {e}")

                if body_text:
                    text_parts.append(body_text)

                # List attachments
                attachments = []
                for part in self._message.iter_parts():
                    if part.get_content_disposition() == 'attachment':
                        filename = part.get_filename()
                        if filename:
                            attachments.append(filename)

                if attachments:
                    text_parts.append("")
                    text_parts.append("[Attachments]")
                    for filename in attachments:
                        text_parts.append(f"- {filename}")

            else:  # MSG file
                text_parts.append("[Email Headers]")
                text_parts.append(f"From: {self._headers.get('from', 'N/A')}")
                text_parts.append(f"To: {self._headers.get('to', 'N/A')}")
                text_parts.append(f"Subject: {self._headers.get('subject', 'N/A')}")
                text_parts.append(f"Date: {self._headers.get('date', 'N/A')}")
                text_parts.append("")
                text_parts.append("[Email Body]")
                text_parts.append(self._body_plain)

            full_text = "\n".join(text_parts)

            logger.info(
                f"Text extraction completed",
                extra={
                    "extra_fields": {
                        "total_length": len(full_text),
                    }
                },
            )

            return full_text

        except Exception as e:
            logger.error(f"Text extraction failed: {e}", exc_info=True)
            raise DocumentProcessingError(
                f"Failed to extract text from email: {str(e)}",
                {"file_path": str(self.file_path)}
            )

    def rebuild(self, anonymized_text: str, detections: List[Dict[str, Any]]) -> bytes:
        """
        Rebuild email with anonymized content.

        Creates a new .eml file with anonymized text.

        Args:
            anonymized_text: Anonymized text
            detections: List of detections (for reference)

        Returns:
            Email file bytes (.eml format)
        """
        try:
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            logger.info("Rebuilding email with anonymized content")

            # Parse anonymized text
            sections = anonymized_text.split("\n\n")

            # Extract headers and body
            headers = {}
            body = ""

            in_headers = False
            in_body = False

            for section in sections:
                if "[Email Headers]" in section:
                    in_headers = True
                    continue
                elif "[Email Body]" in section:
                    in_body = True
                    in_headers = False
                    continue
                elif "[Attachments]" in section:
                    break

                if in_headers:
                    for line in section.split("\n"):
                        if ": " in line:
                            key, value = line.split(": ", 1)
                            headers[key.lower()] = value

                elif in_body:
                    body += section + "\n"

            # Create new email
            msg = MIMEMultipart()

            # Set headers
            if "from" in headers:
                msg['From'] = headers['from']
            if "to" in headers:
                msg['To'] = headers['to']
            if "subject" in headers:
                msg['Subject'] = headers['subject']
            if "date" in headers:
                msg['Date'] = headers['date']

            # Add body
            msg.attach(MIMEText(body.strip(), 'plain'))

            # Convert to bytes
            email_bytes = msg.as_bytes()

            logger.info(
                "Email rebuilt successfully",
                extra={"extra_fields": {"output_size": len(email_bytes)}},
            )

            return email_bytes

        except Exception as e:
            logger.error(f"Email rebuild failed: {e}", exc_info=True)
            raise DocumentProcessingError(
                f"Failed to rebuild email: {str(e)}",
                {"file_path": str(self.file_path)}
            )

    def close(self):
        """Close document resources"""
        if hasattr(self, "_message"):
            self._message = None
            logger.debug("Email document closed")

    def __del__(self):
        """Cleanup on deletion"""
        self.close()
