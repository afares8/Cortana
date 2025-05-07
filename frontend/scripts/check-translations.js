#!/usr/bin/env node

/**
 * Translation Check Script
 * 
 * This script scans React components for potentially hardcoded text
 * and verifies that components are using the translation system.
 * 
 * Usage: node scripts/check-translations.js [directory]
 * Default directory is src/components
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const patterns = [
  /<[^>]*>[A-Z][a-zA-Z\s]+<\/[^>]*>/g,  // JSX elements with capitalized content
  /className="[^"]*">[A-Z][a-zA-Z\s]+</g,  // After className with capitalized content
  /<[^>]*>([A-Z][a-zA-Z\s]+ [A-Za-z\s]+)<\/[^>]*>/g,  // Elements with phrases
  /label="([A-Z][a-zA-Z\s]+)"/g,  // Label attributes with capitalized content
  /placeholder="([A-Z][a-zA-Z\s]+)"/g,  // Placeholder attributes with capitalized content
  /title="([A-Z][a-zA-Z\s]+)"/g,  // Title attributes with capitalized content
];

const exceptions = [
  /<[^>]*>Cortana<\/[^>]*>/g,  // App name
  /<svg/g,  // SVG elements
  /<path/g,  // SVG path elements
  /<circle/g,  // SVG circle elements
  /<rect/g,  // SVG rect elements
  /<Import/g,  // Import statements
  /<React/g,  // React references
  /<Link/g,  // Link components
  /<Route/g,  // Route components
  /<Router/g,  // Router components
  /<Provider/g,  // Provider components
  /<Fragment/g,  // Fragment components
  /<Suspense/g,  // Suspense components
  /<ErrorBoundary/g,  // ErrorBoundary components
  /<[^>]*>\{\s*t\(/g,  // Already using translation function
];

const extensions = ['.tsx', '.jsx'];

const excludeDirs = ['node_modules', 'build', 'dist', '.git', 'coverage', 'public'];

function getComponentFiles(dir) {
  let results = [];
  
  try {
    const list = fs.readdirSync(dir);
    
    list.forEach(file => {
      const filePath = path.join(dir, file);
      const stat = fs.statSync(filePath);
      
      if (stat.isDirectory() && !excludeDirs.includes(file)) {
        results = results.concat(getComponentFiles(filePath));
      } else if (extensions.includes(path.extname(file))) {
        results.push(filePath);
      }
    });
  } catch (err) {
    console.error(`Error reading directory ${dir}: ${err.message}`);
  }
  
  return results;
}

function isException(match, content) {
  for (const exception of exceptions) {
    if (exception.test(match)) {
      return true;
    }
  }
  return false;
}

function checkFile(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    let hasIssues = false;
    let issues = [];
    
    const usesTranslations = content.includes('useTranslation') || 
                            content.includes('i18n.t(') || 
                            content.includes(' t(');
    
    if (!usesTranslations && content.includes('return (')) {
      issues.push('File may not use translations');
      hasIssues = true;
    }
    
    patterns.forEach(pattern => {
      const matches = content.match(pattern);
      if (matches && matches.length > 0) {
        const filteredMatches = matches.filter(match => !isException(match, content));
        
        if (filteredMatches.length > 0) {
          issues.push(`Possible hardcoded text: ${filteredMatches.join(', ')}`);
          hasIssues = true;
        }
      }
    });
    
    return { hasIssues, issues, filePath };
  } catch (err) {
    console.error(`Error checking file ${filePath}: ${err.message}`);
    return { hasIssues: false, issues: [], filePath };
  }
}

function formatFilePath(filePath) {
  const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
  return filePath.replace(projectRoot, '').replace(/^\//, '');
}

function main() {
  const scanDir = process.argv[2] || path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'src', 'components');
  
  console.log(`\n🔍 Checking for potentially hardcoded text in components...`);
  console.log(`📁 Scanning directory: ${formatFilePath(scanDir)}\n`);
  
  const files = getComponentFiles(scanDir);
  
  console.log(`Found ${files.length} component files to check.\n`);
  
  let issuesFound = 0;
  let filesWithIssues = [];
  
  files.forEach(file => {
    const result = checkFile(file);
    if (result.hasIssues) {
      issuesFound += result.issues.length;
      filesWithIssues.push({
        path: formatFilePath(file),
        issues: result.issues
      });
    }
  });
  
  if (filesWithIssues.length > 0) {
    console.log(`⚠️  Found ${issuesFound} potential issues in ${filesWithIssues.length} files:\n`);
    
    filesWithIssues.forEach(file => {
      console.log(`📄 ${file.path}:`);
      file.issues.forEach(issue => {
        console.log(`   - ${issue}`);
      });
      console.log('');
    });
    
    console.log(`\n💡 Recommendations:`);
    console.log(`   - Use the translation function: const { t } = useTranslation();`);
    console.log(`   - Replace hardcoded text with: {t('namespace.key')}`);
    console.log(`   - Add new keys to both en.json and es.json files`);
    console.log(`   - Follow the existing namespace structure for consistency`);
  } else {
    console.log(`✅ No issues found. All components appear to use translations properly.`);
  }
  
  console.log(`\n✨ Translation check completed.\n`);
}

main();
