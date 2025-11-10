const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs').promises;
const sharp = require('sharp');
//const fetch = require('node-fetch');
const fetch = (...args) => import('node-fetch').then(({ default: fetch }) => fetch(...args));

const FormData = require('form-data');
const fsSync = require('fs'); // For createReadStream()
const { validateImage } = require('../middleware/validation');
const { detectBreed } = require('../services/breedDetection');
const { getAdoptionCenters, createBreedSearchUrls } = require('../services/adoptionService');

const router = express.Router();

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const uploadDir = path.join(__dirname, '../uploads');
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, 'breed-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const upload = multer({
  storage: storage,
  limits: {
    fileSize: 10 * 1024 * 1024, // 10MB limit
  },
  fileFilter: (req, file, cb) => {
    const allowedTypes = /jpeg|jpg|png|gif|webp/;
    const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
    const mimetype = allowedTypes.test(file.mimetype);

    if (mimetype && extname) {
      return cb(null, true);
    } else {
      cb(new Error('Only image files are allowed!'));
    }
  }
});



// POST /api/breed/detect - Detect dog breed from uploaded image
// router.post('/detect', upload.single('image'), validateImage, async (req, res) => {
//   try {
//     const imagePath = req.file.path;
    
//     // Process image with sharp for optimization
//     const processedImagePath = await processImage(imagePath);
    
//     // Detect breed
//     const breedResult = await detectBreed(processedImagePath);
    
//     if (breedResult.error) {
//       return res.status(400).json(breedResult);
//     }
    
//     // Get adoption centers for the detected breed
//     const adoptionCenters = await getAdoptionCenters(breedResult.breed);
    
//     // Create breed-specific search URLs
//     const searchUrls = createBreedSearchUrls(breedResult.breed);
    
//     // Clean up temporary files
//     await cleanupFiles([imagePath, processedImagePath]);
    
//     // Return comprehensive result
//     res.json({
//       success: true,
//       breed: breedResult.breed,
//       confidence: breedResult.confidence,
//       adoption_centers: adoptionCenters,
//       direct_search_urls: searchUrls,
//       redirect_info: {
//         petfinder_url: searchUrls.petfinder,
//         adoptapet_url: searchUrls.adoptapet,
//         aspca_url: searchUrls.aspca,
//         note: "Click any URL to search for this breed directly on the adoption website"
//       },
//       message: `Found ${adoptionCenters.length} adoption centers for ${breedResult.breed} dogs`,
//       timestamp: new Date().toISOString()
//     });
    
//   } catch (error) {
//     console.error('Breed detection error:', error);
    
//     // Clean up files on error
//     if (req.file) {
//       try {
//         await fs.unlink(req.file.path);
//       } catch (cleanupError) {
//         console.error('File cleanup error:', cleanupError);
//       }
//     }
    
//     res.status(500).json({
//       success: false,
//       error: 'Breed detection failed',
//       message: 'Unable to process the image. Please try again.',
//       ...(process.env.NODE_ENV === 'development' && { details: error.message })
//     });
//   }
// });


// POST /api/breed/detect - Detect dog breed using Python Flask backend
router.post("/detect", upload.single("image"), validateImage, async (req, res) => {
  try {
    const imagePath = req.file.path;

    // Optional: process image with sharp
    const processedImagePath = await processImage(imagePath);

    // ✅ Send the image to your Python Flask API
    const formData = new FormData();
    formData.append("file", fsSync.createReadStream(processedImagePath));

    const flaskResponse = await fetch("http://localhost:8000/predict", {
      method: "POST",
      body: formData,
      headers: formData.getHeaders(),
    });

    if (!flaskResponse.ok) {
      throw new Error(`Flask API error: ${flaskResponse.statusText}`);
    }

    const breedResult = await flaskResponse.json();
    if (breedResult.error) {
      return res.status(400).json(breedResult);
    }

    // Optional: supplement with Node adoption data (if you want)
    const adoptionCenters = await getAdoptionCenters(breedResult.breed);
    const searchUrls = createBreedSearchUrls(breedResult.breed);
    
    // Delay slightly before cleanup (fixes EBUSY issue on Windows)
    await new Promise(resolve => setTimeout(resolve, 1000));
    // Clean up temporary files
    await cleanupFiles([imagePath, processedImagePath]);

    console.log("CHeck result:",breedResult)

    // ✅ Final response to frontend
    res.json({
      success: true,
      breed: breedResult.breed,
      confidence: breedResult.confidence,
      adoption_centers: breedResult.adoption_centers || adoptionCenters,
      direct_search_urls: breedResult.direct_search_urls || searchUrls,
      redirect_info: breedResult.redirect_info || {
        petfinder_url: searchUrls.petfinder,
        adoptapet_url: searchUrls.adoptapet,
        aspca_url: searchUrls.aspca,
        note: "Click any URL to search for this breed directly on the adoption website",
      },
      message: breedResult.message || `Found ${adoptionCenters.length} adoption centers for ${breedResult.breed} dogs`,
      timestamp: new Date().toISOString(),
    });

  } catch (error) {
    console.error("Breed detection error:", error);

    // Clean up on error
    if (req.file) {
      try {
        await fs.unlink(req.file.path);
      } catch (cleanupError) {
        console.error("File cleanup error:", cleanupError);
      }
    }

    res.status(500).json({
      success: false,
      error: "Breed detection failed",
      message: "Unable to process the image. Please try again.",
      ...(process.env.NODE_ENV === "development" && { details: error.message }),
    });
  }
});

// GET /api/breed/centers/:breed - Get adoption centers for specific breed
router.get('/centers/:breed', async (req, res) => {
  try {
    const { breed } = req.params;
    const adoptionCenters = await getAdoptionCenters(breed);
    const searchUrls = createBreedSearchUrls(breed);
    
    res.json({
      success: true,
      breed: breed,
      adoption_centers: adoptionCenters,
      direct_search_urls: searchUrls,
      count: adoptionCenters.length,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Adoption centers error:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch adoption centers',
      message: 'Unable to retrieve adoption information.'
    });
  }
});

// Helper function to process image
async function processImage(inputPath) {
  const outputPath = inputPath.replace(path.extname(inputPath), '_processed.jpg');
  
  await sharp(inputPath)
    .resize(800, 600, { fit: 'inside', withoutEnlargement: true })
    .jpeg({ quality: 90 })
    .toFile(outputPath);
    
  return outputPath;
}

// Helper function to clean up temporary files
async function cleanupFiles(filePaths) {
  for (const filePath of filePaths) {
    try {
      await fs.unlink(filePath);
    } catch (error) {
      console.error(`Failed to delete file ${filePath}:`, error);
    }
  }
}

module.exports = router;
