const Joi = require('joi');

// Validation schema for image upload
const imageUploadSchema = Joi.object({
  image: Joi.object().required()
});

// Validation schema for breed parameter
const breedParamSchema = Joi.object({
  breed: Joi.string()
    .min(2)
    .max(50)
    .pattern(/^[a-zA-Z\s\-_]+$/)
    .required()
    .messages({
      'string.pattern.base': 'Breed name can only contain letters, spaces, hyphens, and underscores',
      'string.min': 'Breed name must be at least 2 characters long',
      'string.max': 'Breed name must be less than 50 characters'
    })
});

// Middleware to validate image upload
const validateImage = (req, res, next) => {
  if (!req.file) {
    return res.status(400).json({
      success: false,
      error: 'No image file provided',
      message: 'Please upload an image file'
    });
  }

  // Check file size (already handled by multer, but double-check)
  if (req.file.size > 10 * 1024 * 1024) {
    return res.status(413).json({
      success: false,
      error: 'File too large',
      message: 'Maximum file size is 10MB'
    });
  }

  // Check file type
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
  if (!allowedTypes.includes(req.file.mimetype)) {
    return res.status(400).json({
      success: false,
      error: 'Invalid file type',
      message: 'Only JPEG, PNG, GIF, and WebP images are allowed'
    });
  }

  next();
};

// Middleware to validate breed parameter
const validateBreedParam = (req, res, next) => {
  const { error, value } = breedParamSchema.validate(req.params);
  
  if (error) {
    return res.status(400).json({
      success: false,
      error: 'Invalid breed parameter',
      message: error.details[0].message
    });
  }
  
  req.params = value;
  next();
};

// Middleware to validate request body
const validateRequestBody = (schema) => {
  return (req, res, next) => {
    const { error, value } = schema.validate(req.body);
    
    if (error) {
      return res.status(400).json({
        success: false,
        error: 'Invalid request data',
        message: error.details[0].message
      });
    }
    
    req.body = value;
    next();
  };
};

module.exports = {
  validateImage,
  validateBreedParam,
  validateRequestBody,
  imageUploadSchema,
  breedParamSchema
};
