#!/usr/bin/env python3
"""
Example: PDF Document Processing with Anonyma

Demonstrates how to:
1. Process PDF documents (digital and scanned)
2. Extract text with OCR if needed
3. Anonymize PII in PDF
4. Rebuild PDF with anonymized content
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from anonyma_core import AnonymaEngine
from anonyma_core.modes import AnonymizationMode
from anonyma_core.documents import DocumentPipeline


def create_sample_pdf():
    """Create a sample PDF for testing (requires reportlab)"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import inch
    except ImportError:
        print("❌ reportlab not installed. Install with: pip install reportlab")
        return None

    # Sample text with PII
    sample_text = """
    DOCUMENT CONFIDENZIALE

    Informazioni Personali
    ======================

    Nome: Mario Rossi
    Data di nascita: 15/03/1985
    Indirizzo: Via Roma 123, 20100 Milano (MI)

    Contatti
    ========
    Email: mario.rossi@email.com
    Telefono: +39 339 1234567
    Telefono ufficio: +39 02 12345678

    Dati Fiscali
    ============
    Codice Fiscale: RSSMRA85C15H501X
    Partita IVA: 12345678901

    Note
    ====
    Il sig. Rossi è un cliente dal 2015 e ha sempre rispettato
    le scadenze di pagamento. Indirizzo email secondario:
    m.rossi@azienda.it
    """

    output_path = Path("sample_document.pdf")

    try:
        # Create PDF
        doc = SimpleDocTemplate(str(output_path), pagesize=letter)
        story = []
        styles = getSampleStyleSheet()

        # Split into paragraphs
        paragraphs = sample_text.strip().split("\n\n")

        for para_text in paragraphs:
            if para_text.strip():
                para = Paragraph(para_text.replace("\n", "<br/>"), styles["Normal"])
                story.append(para)
                story.append(Spacer(1, 0.2 * inch))

        doc.build(story)

        print(f"✅ Sample PDF created: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Failed to create sample PDF: {e}")
        return None


def process_pdf_example():
    """Example of processing a PDF document"""
    print("=" * 70)
    print("ANONYMA - PDF DOCUMENT PROCESSING EXAMPLE")
    print("=" * 70)
    print()

    # Step 1: Create sample PDF
    print("Step 1: Creating sample PDF...")
    print("-" * 70)
    pdf_path = create_sample_pdf()

    if pdf_path is None:
        print("⚠️  Could not create sample PDF. Make sure reportlab is installed.")
        return

    print()

    # Step 2: Initialize engine and pipeline
    print("Step 2: Initializing Anonyma engine and pipeline...")
    print("-" * 70)

    try:
        # Use basic detector (no Flair) for faster processing
        engine = AnonymaEngine(use_flair=False)
        pipeline = DocumentPipeline(engine)

        print("✅ Engine and pipeline initialized")
        print(f"   Supported formats: {[f.value for f in pipeline.get_supported_formats()]}")
        print()

    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return

    # Step 3: Process PDF with different modes
    print("Step 3: Processing PDF with different anonymization modes...")
    print("-" * 70)
    print()

    modes_to_test = [
        (AnonymizationMode.REDACT, "Redaction mode (block characters)"),
        (AnonymizationMode.SUBSTITUTE, "Substitution mode (fake data)"),
        (AnonymizationMode.VISUAL_REDACT, "Visual redaction mode (heavy blocks)"),
    ]

    for mode, description in modes_to_test:
        print(f"Processing with {description}...")

        try:
            # Process document
            result = pipeline.process(
                file_path=pdf_path,
                mode=mode,
                output_path=Path(f"anonymized_{mode.value}_{pdf_path.name}"),
                language="it",
                save_output=True,
            )

            if result.success:
                print(f"✅ Success!")
                print(f"   - Detections found: {result.detections_count}")
                print(f"   - Processing time: {result.processing_time:.2f}s")
                print(f"   - Output saved to: {result.output_file}")
                print(f"   - Original size: {result.metadata.get('file_size', 0)} bytes")

                # Show detection summary
                if result.detections:
                    entity_types = {}
                    for detection in result.detections:
                        entity_type = detection.get("entity_type", "UNKNOWN")
                        entity_types[entity_type] = entity_types.get(entity_type, 0) + 1

                    print(f"   - Detection summary:")
                    for entity_type, count in sorted(entity_types.items()):
                        print(f"     • {entity_type}: {count}")

            else:
                print(f"❌ Failed: {result.error}")

            print()

        except Exception as e:
            print(f"❌ Error processing with {mode.value}: {e}")
            import traceback

            traceback.print_exc()
            print()

    # Step 4: Show text extraction example
    print("Step 4: Text extraction example...")
    print("-" * 70)

    try:
        from anonyma_core.documents import PDFDocument

        # Load PDF
        pdf_doc = PDFDocument(pdf_path)

        print(f"PDF Metadata:")
        print(f"  - File: {pdf_doc.metadata.file_name}")
        print(f"  - Format: {pdf_doc.metadata.format.value}")
        print(f"  - Pages: {pdf_doc.metadata.page_count}")
        print(f"  - Size: {pdf_doc.metadata.file_size} bytes")
        print(f"  - Is scanned: {pdf_doc.metadata.is_scanned}")
        print()

        # Extract text
        text = pdf_doc.extract_text()
        print(f"Extracted text preview (first 200 chars):")
        print("-" * 70)
        print(text[:200] + "...")
        print()

    except Exception as e:
        print(f"❌ Text extraction failed: {e}")
        print()

    # Summary
    print("=" * 70)
    print("PROCESSING COMPLETE")
    print("=" * 70)
    print()
    print("Output files created:")
    for mode, _ in modes_to_test:
        output_file = Path(f"anonymized_{mode.value}_{pdf_path.name}")
        if output_file.exists():
            print(f"  ✅ {output_file}")
    print()
    print("You can now:")
    print("  1. Open the original PDF to see the source content")
    print("  2. Open the anonymized PDFs to see the results")
    print("  3. Compare the different anonymization modes")
    print()


def main():
    """Main function"""
    try:
        process_pdf_example()
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
