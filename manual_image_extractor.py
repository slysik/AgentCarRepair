#!/usr/bin/env python3
"""
XC60 Owner's Manual Image Extraction System
Extracts images and diagrams from the Volvo XC60 PDF manual for visual enhancement

This module uses PyMuPDF to extract all images from the owner's manual PDF,
organizes them by section, and creates metadata for integration with the RAG system.
"""

import os
import json
import logging
import fitz  # PyMuPDF
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ExtractedImage:
    """Metadata for extracted manual images"""
    page_number: int
    image_index: int
    filename: str
    file_path: str
    width: int
    height: int
    size_bytes: int
    image_type: str
    caption: str = ""
    section: str = ""
    figure_number: str = ""
    keywords: List[str] = None
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []
    
    def to_dict(self) -> Dict:
        return asdict(self)

class ManualImageExtractor:
    """Extract and organize images from XC60 Owner's Manual PDF"""
    
    def __init__(self, pdf_path: str, output_dir: str = "static/manual_images"):
        self.pdf_path = pdf_path
        self.output_dir = Path(output_dir)
        self.images: List[ExtractedImage] = []
        
        # Section keywords for auto-categorization
        self.section_keywords = {
            'engine': ['engine', 'motor', 'oil', 'coolant', 'radiator', 'dipstick'],
            'brakes': ['brake', 'pad', 'disc', 'caliper', 'rotor', 'brake fluid'],
            'electrical': ['fuse', 'battery', 'alternator', 'starter', 'wire', 'electrical'],
            'lights': ['headlight', 'taillight', 'bulb', 'lamp', 'led', 'lighting'],
            'maintenance': ['service', 'maintenance', 'schedule', 'interval', 'replace'],
            'interior': ['seat', 'dashboard', 'console', 'interior', 'cabin'],
            'exterior': ['door', 'hood', 'trunk', 'bumper', 'mirror', 'exterior'],
            'wheels': ['wheel', 'tire', 'rim', 'pressure', 'rotation'],
            'safety': ['airbag', 'seatbelt', 'warning', 'safety', 'emergency'],
            'transmission': ['transmission', 'gear', 'clutch', 'shift', 'drivetrain']
        }
    
    def extract_images(self) -> List[ExtractedImage]:
        """Extract all images from the PDF manual"""
        logger.info(f"Starting image extraction from {self.pdf_path}")
        
        if not os.path.exists(self.pdf_path):
            raise FileNotFoundError(f"PDF manual not found: {self.pdf_path}")
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Open PDF
        doc = fitz.open(self.pdf_path)
        logger.info(f"PDF opened: {doc.page_count} pages")
        
        total_images = 0
        
        for page_num in range(doc.page_count):
            page = doc[page_num]
            page_images = self._extract_page_images(page, page_num + 1)
            total_images += len(page_images)
            self.images.extend(page_images)
            
            if (page_num + 1) % 50 == 0:
                logger.info(f"Processed {page_num + 1}/{doc.page_count} pages, found {total_images} images")
        
        doc.close()
        
        logger.info(f"Image extraction completed: {len(self.images)} images extracted")
        return self.images
    
    def _extract_page_images(self, page: fitz.Page, page_number: int) -> List[ExtractedImage]:
        """Extract images from a single page"""
        page_images = []
        image_list = page.get_images(full=True)
        
        if not image_list:
            return page_images
        
        # Get page text for context analysis
        page_text = page.get_text().lower()
        
        for img_index, img in enumerate(image_list):
            try:
                # Extract image data
                xref = img[0]
                pix = fitz.Pixmap(page.parent, xref)
                
                # Skip tiny images (likely decorative)
                if pix.width < 50 or pix.height < 50:
                    pix = None
                    continue
                
                # Generate filename
                image_hash = hashlib.md5(pix.tobytes()).hexdigest()[:8]
                filename = f"page_{page_number:03d}_img_{img_index:02d}_{image_hash}.png"
                
                # Determine section based on page content
                section = self._categorize_image(page_text, page_number)
                
                # Create section subdirectory
                section_dir = self.output_dir / section
                section_dir.mkdir(exist_ok=True)
                
                file_path = section_dir / filename
                relative_path = f"/static/manual_images/{section}/{filename}"
                
                # Save image
                if pix.n - pix.alpha < 4:  # GRAY or RGB
                    pix.save(str(file_path))
                else:  # CMYK: convert to RGB first
                    pix1 = fitz.Pixmap(fitz.csRGB, pix)
                    pix1.save(str(file_path))
                    pix1 = None
                
                # Extract caption and figure number from surrounding text
                caption, figure_num = self._extract_caption(page_text, page_number, img_index)
                
                # Generate keywords
                keywords = self._generate_keywords(page_text, section)
                
                # Create image metadata
                extracted_image = ExtractedImage(
                    page_number=page_number,
                    image_index=img_index,
                    filename=filename,
                    file_path=relative_path,
                    width=pix.width,
                    height=pix.height,
                    size_bytes=len(pix.tobytes()),
                    image_type="PNG",
                    caption=caption,
                    section=section,
                    figure_number=figure_num,
                    keywords=keywords
                )
                
                page_images.append(extracted_image)
                logger.debug(f"Extracted image: {filename} from page {page_number}")
                
                pix = None
                
            except Exception as e:
                logger.warning(f"Failed to extract image {img_index} from page {page_number}: {e}")
                continue
        
        return page_images
    
    def _categorize_image(self, page_text: str, page_number: int) -> str:
        """Categorize image based on page content and location"""
        # Count keyword matches for each section
        section_scores = {}
        
        for section, keywords in self.section_keywords.items():
            score = sum(1 for keyword in keywords if keyword in page_text)
            if score > 0:
                section_scores[section] = score
        
        # Return section with highest score, or 'general' if no matches
        if section_scores:
            return max(section_scores.items(), key=lambda x: x[1])[0]
        
        # Page-based fallback categorization
        if page_number < 50:
            return 'introduction'
        elif page_number < 100:
            return 'controls'
        elif page_number < 200:
            return 'operation'
        elif page_number < 300:
            return 'maintenance'
        else:
            return 'general'
    
    def _extract_caption(self, page_text: str, page_number: int, img_index: int) -> Tuple[str, str]:
        """Extract image caption and figure number from page text"""
        # Look for figure references like "Figure 3.2", "Fig. 5-1", etc.
        figure_patterns = [
            r'[Ff]igure?\s*(\d+[-.]?\d*)\s*[:-]?\s*([^.]+)',
            r'[Ff]ig\.?\s*(\d+[-.]?\d*)\s*[:-]?\s*([^.]+)',
            r'(\d+[-.]?\d*)\s*[:-]?\s*([^.]+diagram|illustration|image)'
        ]
        
        caption = f"Manual illustration from page {page_number}"
        figure_num = ""
        
        for pattern in figure_patterns:
            matches = re.finditer(pattern, page_text, re.IGNORECASE)
            for match in matches:
                figure_num = match.group(1)
                potential_caption = match.group(2).strip()[:100]  # Limit length
                if len(potential_caption) > 10:  # Reasonable caption length
                    caption = potential_caption
                    break
            if figure_num:
                break
        
        return caption, figure_num
    
    def _generate_keywords(self, page_text: str, section: str) -> List[str]:
        """Generate keywords for image search"""
        keywords = [section]
        
        # Add section-specific keywords that appear in text
        if section in self.section_keywords:
            for keyword in self.section_keywords[section]:
                if keyword in page_text:
                    keywords.append(keyword)
        
        # Add common automotive terms found in text
        automotive_terms = [
            'bolt', 'screw', 'connector', 'housing', 'assembly', 'component',
            'location', 'position', 'arrow', 'diagram', 'illustration'
        ]
        
        for term in automotive_terms:
            if term in page_text:
                keywords.append(term)
        
        return list(set(keywords))  # Remove duplicates
    
    def save_metadata(self, output_file: str = "manual_images_metadata.json"):
        """Save extracted image metadata to JSON file"""
        metadata_path = self.output_dir / output_file
        
        metadata = {
            'pdf_source': self.pdf_path,
            'extraction_timestamp': __import__('datetime').datetime.now().isoformat(),
            'total_images': len(self.images),
            'images': [img.to_dict() for img in self.images],
            'sections': list(set(img.section for img in self.images))
        }
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Metadata saved to {metadata_path}")
        return metadata_path
    
    def get_section_summary(self) -> Dict[str, int]:
        """Get summary of images by section"""
        summary = {}
        for image in self.images:
            summary[image.section] = summary.get(image.section, 0) + 1
        return summary

def main():
    """Extract images from XC60 manual"""
    pdf_path = "/Users/slysik/Downloads/XC60_OwnersManual_MY21_en-US_TP32027 (1).pdf"
    
    if not os.path.exists(pdf_path):
        logger.error(f"PDF manual not found: {pdf_path}")
        return
    
    extractor = ManualImageExtractor(pdf_path)
    
    try:
        # Extract images
        images = extractor.extract_images()
        
        # Save metadata
        extractor.save_metadata()
        
        # Print summary
        summary = extractor.get_section_summary()
        logger.info("Image extraction summary:")
        for section, count in sorted(summary.items()):
            logger.info(f"  {section}: {count} images")
        
        logger.info(f"✅ Successfully extracted {len(images)} images")
        
    except Exception as e:
        logger.error(f"❌ Image extraction failed: {e}")
        raise

if __name__ == "__main__":
    main()