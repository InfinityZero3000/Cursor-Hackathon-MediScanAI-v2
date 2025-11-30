const fs = require('fs');
const path = require('path');
const { parse } = require('csv-parse/sync');

// Cache for drug database
let drugDatabase = null;
let drugDatabasePath = null;

/**
 * Get drug database (cached)
 */
function getDrugDatabase() {
  if (drugDatabase !== null) {
    return drugDatabase;
  }

  // Try different possible paths - prioritize drug_database_refined.csv
  const possiblePaths = [
    path.join(__dirname, '..', 'Crawldata', 'drug_database_refined.csv'),
    path.join(process.cwd(), 'Crawldata', 'drug_database_refined.csv'),
    // Fallback to drug_index.csv if refined not found
    path.join(__dirname, '..', 'Crawldata', 'drug_index.csv'),
    path.join(process.cwd(), 'Crawldata', 'drug_index.csv'),
  ];

  for (const dbPath of possiblePaths) {
    if (fs.existsSync(dbPath)) {
      drugDatabasePath = dbPath;
      try {
        const fileContent = fs.readFileSync(dbPath, 'utf-8');
        const records = parse(fileContent, {
          columns: true,
          skip_empty_lines: true,
          trim: true,
          relax_column_count: true,
          quote: '"',
          escape: '"',
        });
        drugDatabase = records;
        console.log(`✅ Loaded ${drugDatabase.length} drugs from database`);
        return drugDatabase;
      } catch (error) {
        console.error(`⚠️ Error loading database from ${dbPath}:`, error);
      }
    }
  }

  // Return empty array if database not found
  console.warn('⚠️ Drug database not found, returning empty array');
  drugDatabase = [];
  return drugDatabase;
}

/**
 * Search drug in database
 */
function searchDrugInDatabase(drugName) {
  const db = getDrugDatabase();

  if (!db || db.length === 0) {
    return null;
  }

  const drugNameLower = drugName.toLowerCase().trim();

  // Exact match
  const exactMatch = db.find(
    (drug) => drug.DrugName && drug.DrugName.toLowerCase() === drugNameLower
  );
  if (exactMatch) {
    return exactMatch;
  }

  // Partial match
  const partialMatch = db.find(
    (drug) =>
      drug.DrugName &&
      drug.DrugName.toLowerCase().includes(drugNameLower)
  );
  if (partialMatch) {
    return partialMatch;
  }

  // Keyword match
  const keywords = drugNameLower.split(' ').filter((k) => k.length > 3);
  for (const keyword of keywords) {
    const keywordMatch = db.find(
      (drug) =>
        drug.DrugName &&
        drug.DrugName.toLowerCase().includes(keyword)
    );
    if (keywordMatch) {
      return keywordMatch;
    }
  }

  return null;
}

/**
 * Search drugs by query
 */
function searchDrugs(query, limit = 20) {
  const db = getDrugDatabase();

  if (!db || db.length === 0) {
    return [];
  }

  const queryLower = query.toLowerCase();
  const results = db
    .filter(
      (drug) =>
        drug.DrugName &&
        drug.DrugName.toLowerCase().includes(queryLower)
    )
    .slice(0, limit);

  return results;
}

module.exports = {
  getDrugDatabase,
  searchDrugInDatabase,
  searchDrugs,
};

