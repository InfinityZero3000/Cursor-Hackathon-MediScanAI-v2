const functions = require('firebase-functions');
const admin = require('firebase-admin');
const cors = require('cors')({ origin: true });
const { searchDrugInDatabase, searchDrugs } = require('./utils');

// Initialize Firebase Admin (optional, for Firestore if needed)
if (!admin.apps.length) {
  admin.initializeApp();
}

// Health check endpoint
exports.health = functions.https.onRequest((req, res) => {
  return cors(req, res, () => {
    res.json({
      status: 'ok',
      message: 'Firebase Functions API is running',
      timestamp: new Date().toISOString()
    });
  });
});

// Scan drug from image
exports.scan = functions.https.onRequest((req, res) => {
  return cors(req, res, async () => {
    if (req.method !== 'POST') {
      return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
      const { image } = req.body;

      if (!image) {
        return res.status(400).json({ error: 'No image provided' });
      }

      // TODO: Implement image processing and OCR
      // For now, return placeholder
      // You can integrate with external OCR service or use a library
      
      const extractedText = 'Panadol Extra'; // Placeholder - replace with actual OCR
      
      // Search in database
      const drugInfo = searchDrugInDatabase(extractedText);

      if (drugInfo) {
        // Determine RX status from Is_Prescription field
        const isPrescription = drugInfo.Is_Prescription === 'True' || drugInfo.Is_Prescription === true;
        const rxStatus = isPrescription ? 'RX' : 'OTC';
        
        return res.json({
          success: true,
          drug_name: drugInfo.DrugName || '',
          active_ingredient: drugInfo.ActiveIngredient || '',
          page_number: drugInfo.PageNumber || '',
          category: drugInfo.Category || '',
          extracted_text: extractedText,
          rx_status: rxStatus,
          is_prescription: isPrescription
        });
      } else {
        return res.status(404).json({
          success: false,
          message: 'Không tìm thấy thông tin thuốc trong database',
          extracted_text: extractedText
        });
      }

    } catch (error) {
      console.error('Error processing scan:', error);
      return res.status(500).json({
        error: 'Internal server error',
        message: error.message
      });
    }
  });
});

// Search drugs
exports.searchDrugs = functions.https.onRequest((req, res) => {
  return cors(req, res, async () => {
    if (req.method !== 'GET') {
      return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
      const query = req.query.q;

      if (!query) {
        return res.status(400).json({ error: 'Query parameter required' });
      }

      // Search in database
      const results = searchDrugs(query, 20);
      
      return res.json({
        drugs: results
      });

    } catch (error) {
      console.error('Error searching drugs:', error);
      return res.status(500).json({
        error: 'Internal server error',
        message: error.message
      });
    }
  });
});

