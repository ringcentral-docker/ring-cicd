#!/usr/bin/env python3
"""
Jacoco to Cobertura Coverage Report Converter
Convert Jacoco XML reports to GitLab-compatible Cobertura format
"""

import xml.etree.ElementTree as ET
import sys
import os
import json
from pathlib import Path
import re


def convert_jacoco_to_cobertura(jacoco_path, cobertura_path):
    """
    Convert Jacoco XML report to Cobertura XML format
    
    Args:
        jacoco_path (str): Input jacoco report file path
        cobertura_path (str): Output cobertura report file path
    
    Returns:
        bool: Whether conversion was successful
    """
    try:
        # Check if input file exists
        if not os.path.exists(jacoco_path):
            print(f"Error: Jacoco report file not found: {jacoco_path}")
            return False
        
        # Parse jacoco XML report
        tree = ET.parse(jacoco_path)
        root = tree.getroot()
        
        # Extract coverage data
        instruction_covered = 0
        instruction_missed = 0
        line_covered = 0
        line_missed = 0
        branch_covered = 0
        branch_missed = 0
        
        # Extract coverage data from all counters
        for counter in root.findall('.//counter'):
            counter_type = counter.get('type')
            covered = int(counter.get('covered', 0))
            missed = int(counter.get('missed', 0))
            
            if counter_type == 'INSTRUCTION':
                instruction_covered += covered
                instruction_missed += missed
            elif counter_type == 'LINE':
                line_covered += covered
                line_missed += missed
            elif counter_type == 'BRANCH':
                branch_covered += covered
                branch_missed += missed
        
        # Calculate coverage rates
        total_instructions = instruction_covered + instruction_missed
        instruction_rate = instruction_covered / total_instructions if total_instructions > 0 else 0
        
        total_lines = line_covered + line_missed
        line_rate = line_covered / total_lines if total_lines > 0 else 0
        
        total_branches = branch_covered + branch_missed
        branch_rate = branch_covered / total_branches if total_branches > 0 else 0
        
        print(f"Coverage statistics:")
        print(f"  Instructions: {instruction_covered} covered, {instruction_missed} missed, {total_instructions} total, rate: {instruction_rate:.4f}")
        print(f"  Lines: {line_covered} covered, {line_missed} missed, {total_lines} total, rate: {line_rate:.4f}")
        print(f"  Branches: {branch_covered} covered, {branch_missed} missed, {total_branches} total, rate: {branch_rate:.4f}")
        
        # Extract package and class information
        packages = {}
        
        for package in root.findall('.//package'):
            package_name = package.get('name', '').replace('/', '.')
            if package_name.startswith('.'):
                package_name = package_name[1:]
            
            if not package_name:
                package_name = 'default'
            
            packages[package_name] = {
                'classes': {},
                'line_rate': 0,
                'branch_rate': 0,
                'complexity': 0
            }
            
            for cls in package.findall('./class'):
                class_name = cls.get('name', '').split('/')[-1]
                file_name = cls.get('sourcefilename', class_name + '.java')
                
                # Skip classes without source file
                if not file_name:
                    continue
                
                # Calculate class coverage
                class_instruction_covered = 0
                class_instruction_missed = 0
                class_branch_covered = 0
                class_branch_missed = 0
                class_line_covered = 0
                class_line_missed = 0
                
                for counter in cls.findall('./counter'):
                    counter_type = counter.get('type')
                    covered = int(counter.get('covered', 0))
                    missed = int(counter.get('missed', 0))
                    
                    if counter_type == 'INSTRUCTION':
                        class_instruction_covered = covered
                        class_instruction_missed = missed
                    elif counter_type == 'LINE':
                        class_line_covered = covered
                        class_line_missed = missed
                    elif counter_type == 'BRANCH':
                        class_branch_covered = covered
                        class_branch_missed = missed
                
                class_total_lines = class_line_covered + class_line_missed
                class_line_rate = class_line_covered / class_total_lines if class_total_lines > 0 else 0
                
                class_total_branches = class_branch_covered + class_branch_missed
                class_branch_rate = class_branch_covered / class_total_branches if class_total_branches > 0 else 0
                
                packages[package_name]['classes'][class_name] = {
                    'filename': file_name,
                    'line_rate': class_line_rate,
                    'branch_rate': class_branch_rate,
                    'complexity': 0
                }
        
        # Create cobertura XML
        cobertura_root = ET.Element('coverage')
        cobertura_root.set('line-rate', f"{line_rate:.4f}")
        cobertura_root.set('branch-rate', f"{branch_rate:.4f}")
        cobertura_root.set('lines-covered', str(line_covered))
        cobertura_root.set('lines-valid', str(total_lines))
        cobertura_root.set('branches-covered', str(branch_covered))
        cobertura_root.set('branches-valid', str(total_branches))
        cobertura_root.set('complexity', '0')
        cobertura_root.set('version', '1.0')
        cobertura_root.set('timestamp', '0')
        
        # Add sources
        sources = ET.SubElement(cobertura_root, 'sources')
        source = ET.SubElement(sources, 'source')
        source.text = '.'
        
        # Add packages
        packages_elem = ET.SubElement(cobertura_root, 'packages')
        
        for pkg_name, pkg_data in packages.items():
            package_elem = ET.SubElement(packages_elem, 'package')
            package_elem.set('name', pkg_name)
            package_elem.set('line-rate', f"{line_rate:.4f}")
            package_elem.set('branch-rate', f"{branch_rate:.4f}")
            package_elem.set('complexity', '0')
            
            classes_elem = ET.SubElement(package_elem, 'classes')
            
            for cls_name, cls_data in pkg_data['classes'].items():
                class_elem = ET.SubElement(classes_elem, 'class')
                class_elem.set('name', cls_name)
                class_elem.set('filename', cls_data['filename'])
                class_elem.set('line-rate', f"{cls_data['line_rate']:.4f}")
                class_elem.set('branch-rate', f"{cls_data['branch_rate']:.4f}")
                class_elem.set('complexity', '0')
                
                # Add empty methods and lines sections (required by schema)
                ET.SubElement(class_elem, 'methods')
                ET.SubElement(class_elem, 'lines')
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(cobertura_path), exist_ok=True)
        
        # Write cobertura report
        tree = ET.ElementTree(cobertura_root)
        tree.write(cobertura_path, encoding='utf-8', xml_declaration=True)
        
        print(f"Successfully converted jacoco to cobertura: {cobertura_path}")
        return True
        
    except ET.ParseError as e:
        print(f"Error parsing jacoco XML: {e}")
        return False
    except Exception as e:
        print(f"Conversion failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) != 3:
        print("Usage: python3 jacoco_to_cobertura.py <jacoco_input_path> <cobertura_output_path>")
        print("Example: python3 jacoco_to_cobertura.py reports/jacoco-api/test/jacocoAPITestReport.xml reports/cobertura-api/coverage.xml")
        sys.exit(1)
    
    jacoco_input = sys.argv[1]
    cobertura_output = sys.argv[2]
    
    print(f"Converting jacoco report: {jacoco_input}")
    print(f"Output cobertura report: {cobertura_output}")
    
    success = convert_jacoco_to_cobertura(jacoco_input, cobertura_output)
    
    if success:
        print("Jacoco to Cobertura conversion completed successfully")
        sys.exit(0)
    else:
        print("Jacoco to Cobertura conversion failed")
        # Create a minimal valid cobertura report to prevent pipeline failure
        try:
            os.makedirs(os.path.dirname(cobertura_output), exist_ok=True)
            with open(cobertura_output, 'w') as f:
                f.write('''<?xml version="1.0" ?>
<coverage line-rate="0.0" branch-rate="0.0" lines-covered="0" lines-valid="1" branches-covered="0" branches-valid="0" complexity="0" version="1.0" timestamp="0">
  <sources>
    <source>.</source>
  </sources>
  <packages>
    <package name="default" line-rate="0.0" branch-rate="0.0" complexity="0">
      <classes>
        <class name="default" filename="default" line-rate="0.0" branch-rate="0.0" complexity="0">
          <methods></methods>
          <lines></lines>
        </class>
      </classes>
    </package>
  </packages>
</coverage>''')
            print("Created minimal valid cobertura report as fallback")
        except Exception as e:
            print(f"Failed to create fallback report: {e}")
        
        sys.exit(1)


if __name__ == "__main__":
    main()