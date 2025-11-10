// Adoption centers database and services
const ADOPTION_CENTERS = {
  general: [
    {
      name: "American Society for the Prevention of Cruelty to Animals (ASPCA)",
      website: "https://www.aspca.org/adopt-pet",
      phone: "1-800-628-0028",
      location: "National (Multiple Locations)",
      description: "Leading animal welfare organization with adoption centers nationwide"
    },
    {
      name: "Humane Society of the United States",
      website: "https://www.humanesociety.org/adopt",
      phone: "1-202-452-1100",
      location: "National (Multiple Locations)",
      description: "Comprehensive animal welfare organization with local chapters"
    },
    {
      name: "Petfinder",
      website: "https://www.petfinder.com",
      phone: "N/A",
      location: "Online Platform",
      description: "Largest online database of adoptable pets from shelters and rescues"
    },
    {
      name: "Adopt-a-Pet.com",
      website: "https://www.adoptapet.com",
      phone: "N/A",
      location: "Online Platform",
      description: "Free online service to help find adoptable pets"
    }
  ],
  breed_specific: {
    "german_shepherd": [
      {
        name: "German Shepherd Rescue of Orange County",
        website: "https://www.gsroc.org",
        phone: "1-714-974-7762",
        location: "Orange County, CA",
        description: "Specialized rescue for German Shepherds"
      }
    ],
    "golden_retriever": [
      {
        name: "Golden Retriever Rescue of the Rockies",
        website: "https://www.goldenrescue.com",
        phone: "1-303-279-2400",
        location: "Colorado, USA",
        description: "Specialized rescue for Golden Retrievers"
      },
      {
        name: "Golden Retriever Club of America Rescue",
        website: "https://www.grca.org/rescue",
        phone: "N/A",
        location: "National",
        description: "Official breed club rescue network"
      }
    ],
    "labrador_retriever": [
      {
        name: "Labrador Retriever Rescue",
        website: "https://www.labrescue.org",
        phone: "1-800-555-0123",
        location: "National",
        description: "Dedicated to rescuing and rehoming Labrador Retrievers"
      }
    ],
    "bulldog": [
      {
        name: "Bulldog Club of America Rescue",
        website: "https://www.bcarescue.org",
        phone: "N/A",
        location: "National",
        description: "Official breed club rescue for Bulldogs"
      }
    ],
    "poodle": [
      {
        name: "Poodle Rescue of New England",
        website: "https://www.poodlerescueofnewengland.org",
        phone: "1-617-555-0123",
        location: "New England",
        description: "Rescue organization for Poodles of all sizes"
      }
    ]
  }
};

function createBreedSearchUrls(breedName) {
  const breedEncoded = encodeURIComponent(breedName);
  
  return {
    petfinder: `https://www.petfinder.com/search/dogs-for-adoption/?breed=${breedEncoded}`,
    adoptapet: `https://www.adoptapet.com/s/adoptable-dogs?breed=${breedEncoded}`,
    aspca: `https://www.aspca.org/adopt-pet?animal=dog&breed=${breedEncoded}`,
    humane_society: `https://www.humanesociety.org/adopt?animal=dog&breed=${breedEncoded}`,
    petsmart_charities: `https://www.petsmartcharities.org/adopt-a-pet?animal=dog&breed=${breedEncoded}`,
    rescue_me: `https://www.rescueme.org/dog?breed=${breedEncoded}`,
    akc_rescue: `https://www.akc.org/rescue-network/?breed=${breedEncoded}`
  };
}

async function getAdoptionCenters(breedName) {
  const breedLower = breedName.toLowerCase().replace(/\s+/g, '_');
  
  // Get breed-specific centers if available
  let breedCenters = [];
  if (breedLower in ADOPTION_CENTERS.breed_specific) {
    breedCenters = ADOPTION_CENTERS.breed_specific[breedLower];
  }
  
  // Always include general centers
  const generalCenters = ADOPTION_CENTERS.general;
  
  // Create breed-specific search URLs
  const searchUrls = createBreedSearchUrls(breedName);
  
  // Enhance centers with direct search URLs
  const enhancedCenters = [];
  
  // Add breed-specific centers with search URLs
  for (const center of breedCenters) {
    const enhancedCenter = {
      ...center,
      direct_search_url: searchUrls.petfinder,
      search_available: true
    };
    enhancedCenters.push(enhancedCenter);
  }
  
  // Add general centers with search URLs
  for (const center of generalCenters) {
    const enhancedCenter = {
      ...center,
      direct_search_url: getCenterSearchUrl(center, searchUrls),
      search_available: true
    };
    enhancedCenters.push(enhancedCenter);
  }
  
  // Add additional search platforms
  const additionalPlatforms = [
    {
      name: "PetSmart Charities",
      website: "https://www.petsmartcharities.org",
      direct_search_url: searchUrls.petsmart_charities,
      phone: "1-800-745-2275",
      location: "National",
      description: "PetSmart's charitable foundation with adoption centers",
      search_available: true
    },
    {
      name: "Rescue Me",
      website: "https://www.rescueme.org",
      direct_search_url: searchUrls.rescue_me,
      phone: "N/A",
      location: "Online Platform",
      description: "Direct-to-adopter rescue platform",
      search_available: true
    }
  ];
  
  enhancedCenters.push(...additionalPlatforms);
  
  // Shuffle and return top 5 centers
  const shuffled = enhancedCenters.sort(() => Math.random() - 0.5);
  return shuffled.slice(0, 5);
}

function getCenterSearchUrl(center, searchUrls) {
  const name = center.name.toLowerCase();
  
  if (name.includes('petfinder')) {
    return searchUrls.petfinder;
  } else if (name.includes('adopt-a-pet')) {
    return searchUrls.adoptapet;
  } else if (name.includes('aspca')) {
    return searchUrls.aspca;
  } else if (name.includes('humane society')) {
    return searchUrls.humane_society;
  } else {
    return center.website;
  }
}

async function getAllAdoptionCenters() {
  return {
    general_centers: ADOPTION_CENTERS.general,
    breed_specific_centers: Object.keys(ADOPTION_CENTERS.breed_specific),
    total_centers: ADOPTION_CENTERS.general.length + 
                  Object.values(ADOPTION_CENTERS.breed_specific).flat().length
  };
}

module.exports = {
  getAdoptionCenters,
  createBreedSearchUrls,
  getAllAdoptionCenters
};
