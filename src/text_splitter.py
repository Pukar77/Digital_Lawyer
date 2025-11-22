import re

class ConstitutionSplitter:
    def __init__(self, document_title: str):
        
        self.document_title = document_title
        
        self.part_detect_pattern = r'(Part-\d+)'
        self.split_pattern = r'(?m)^(Part-\d+)'
        self.article_pattern = r'(?m)^(Article\s+\d+)' # Article splitter pattern

    def preprocess_text(self, text):
        """Ensures every 'Part-X' is on its own new line and normalized to 'Part-X'."""
        
        def normalize_header(match):
            # Already in "Part-X" format, just ensure surrounding newlines
            return f"\n\n{match.group(0)}\n"

        # Only normalize strict "Part-X" format (with hyphen)
        cleaned_text = re.sub(self.part_detect_pattern, normalize_header, text, flags=re.IGNORECASE)
        return cleaned_text

    def split_and_chunk(self, text):
        print(f"✂️ Starting chunking for document: **{self.document_title}**")
        
        # Step 1: Clean and normalize text structure
        clean_text = self.preprocess_text(text)
        
        # Step 2: Split the entire document by Part
        segments = re.split(self.split_pattern, clean_text)
        
        final_chunks = []
        current_part = "Preamble" # Default context

        for segment in segments:
            segment = segment.strip()
            if not segment: continue

            # If segment is a Part Header (e.g., "Part-1")
            if re.match(r'^Part-\d+$', segment):
                current_part = segment
            else:
                # If segment is content, delegate to the Article-level splitter
                self._chunk_by_article(segment, current_part, final_chunks)
                
        return final_chunks

    def _chunk_by_article(self, text, part_name, results_list):
        # 🎯 Granularity Requirement: Chunk by Article for maximum semantic coherence
        
        articles = re.split(self.article_pattern, text)
        current_article = "General Provision" # Default context within a Part

        for segment in articles:
            segment = segment.strip()
            if not segment: continue

            # If segment is an Article Header (e.g., "Article 16")
            if re.match(r'^Article\s+\d+$', segment, re.IGNORECASE):
                current_article = segment
            elif len(segment) > 20:
                # This segment is the actual content for the current Article
                
                # 1. METADATA ENRICHMENT: Store mandatory fields
                metadata = {
                    "document_title": self.document_title, # Mandatory Field
                    "part_number": part_name,              # Mandatory Field
                    "article_number": current_article,     # Mandatory Field
                    # Future Extension: "section_clause": "..." (If you add a deeper regex)
                }

                # Create the final chunk structure
                chunk_text = f"{part_name} - {current_article}: {segment}"
                
                results_list.append({
                    "text": chunk_text,
                    "metadata": metadata
                })