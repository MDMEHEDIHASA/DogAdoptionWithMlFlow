const express = require('express');
const { getAdoptionCenters, createBreedSearchUrls, getAllAdoptionCenters } = require('../services/adoptionService');

const router = express.Router();

// GET /api/adoption/centers - Get all available adoption centers
router.get('/centers', async (req, res) => {
  try {
    const allCenters = await getAllAdoptionCenters();
    
    res.json({
      success: true,
      data: allCenters,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Get all centers error:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch adoption centers',
      message: 'Unable to retrieve adoption center information.'
    });
  }
});

// GET /api/adoption/centers/:breed - Get adoption centers for specific breed
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
      message: 'Unable to retrieve adoption information for this breed.'
    });
  }
});

// GET /api/adoption/search-urls/:breed - Get search URLs for specific breed
router.get('/search-urls/:breed', async (req, res) => {
  try {
    const { breed } = req.params;
    const searchUrls = createBreedSearchUrls(breed);
    
    res.json({
      success: true,
      breed: breed,
      search_urls: searchUrls,
      message: `Direct search URLs for ${breed} dogs`,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Search URLs error:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to generate search URLs',
      message: 'Unable to create breed-specific search links.'
    });
  }
});

// GET /api/adoption/redirect/:breed - Redirect to adoption site with breed search
router.get('/redirect/:breed', (req, res) => {
  try {
    const { breed } = req.params;
    const searchUrls = createBreedSearchUrls(breed);
    
    // Default to Petfinder as it's the most popular
    const redirectUrl = searchUrls.petfinder || 'https://www.petfinder.com';
    
    res.redirect(302, redirectUrl);
  } catch (error) {
    console.error('Redirect error:', error);
    res.status(500).json({
      success: false,
      error: 'Redirect failed',
      message: 'Unable to redirect to adoption site.'
    });
  }
});

module.exports = router;
