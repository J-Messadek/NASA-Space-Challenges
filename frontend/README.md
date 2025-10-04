# NASA Space Biology Publications Frontend

A modern React-based web application for exploring and searching through NASA Space Biology research publications.

## Features

- 🔍 **Advanced Search**: Search by title, authors, keywords, summary, or impact
- 🏷️ **Smart Filtering**: Filter by research theme and journal
- 📊 **Rich Data Display**: Shows summaries, impact assessments, themes, and keywords
- 📱 **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- 🎨 **Modern UI**: Beautiful gradient design with smooth animations
- ⚡ **Fast Performance**: Optimized for quick loading and smooth interactions

## Quick Start

### Prerequisites

- Node.js (version 14 or higher)
- npm or yarn

### Installation

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

4. **Open your browser:**
   The app will automatically open at `http://localhost:3000`

### Building for Production

```bash
npm run build
```

This creates an optimized production build in the `build` folder.

## Data Setup

The frontend expects the NASA publications data to be available as a JSON file. Make sure you have:

1. **Generated the publications data** using the Python scraper:
   ```bash
   python main.py
   ```

2. **Copied the JSON file** to the frontend public folder:
   ```bash
   cp nasa_space_biology_publications.json frontend/public/
   ```

## Usage

### Searching Publications

- **Text Search**: Use the search bar to find publications by any text content
- **Theme Filter**: Filter by research themes like "Microgravity Effects", "Space Radiation", etc.
- **Journal Filter**: Filter by specific journals
- **Clear Filters**: Reset all filters to see all publications

### Publication Cards

Each publication card displays:
- **Title**: Full publication title
- **Theme**: AI-generated research theme
- **Authors**: Author list (truncated if many)
- **Journal**: Publication journal
- **Date**: Publication date
- **DOI**: Digital Object Identifier
- **Summary**: AI-generated summary
- **Impact**: Research impact assessment
- **Keywords**: Relevant keywords
- **Actions**: Links to read the full paper

## Project Structure

```
frontend/
├── public/
│   ├── index.html
│   └── nasa_space_biology_publications.json  # Data file
├── src/
│   ├── App.js          # Main application component
│   ├── App.css         # Component-specific styles
│   ├── index.js        # React entry point
│   └── index.css       # Global styles
├── package.json        # Dependencies and scripts
└── README.md          # This file
```

## Technologies Used

- **React 18**: Modern React with hooks
- **Lucide React**: Beautiful icon library
- **CSS3**: Modern styling with gradients and animations
- **Responsive Design**: Mobile-first approach

## Customization

### Styling

The app uses CSS custom properties and can be easily customized:

- **Colors**: Modify the gradient colors in `index.css`
- **Layout**: Adjust the grid and spacing in the CSS files
- **Typography**: Change fonts and sizes in the global styles

### Data Format

The app expects publications data in this format:

```json
[
  {
    "index": 0,
    "title": "Publication Title",
    "authors": ["Author 1", "Author 2"],
    "abstract": "Full abstract text...",
    "summary": "AI-generated summary...",
    "impact": "Research impact assessment...",
    "theme": "Research Theme",
    "keywords": ["keyword1", "keyword2"],
    "doi": "10.1234/example.doi",
    "publication_date": "2023-01-01",
    "journal": "Journal Name",
    "url": "https://example.com/paper"
  }
]
```

## Development

### Available Scripts

- `npm start`: Start development server
- `npm build`: Build for production
- `npm test`: Run tests
- `npm eject`: Eject from Create React App

### Adding New Features

1. **New Filters**: Add filter options in the `App.js` component
2. **New Data Fields**: Update the `PublicationCard` component
3. **New Styling**: Modify the CSS files
4. **New Functionality**: Add new components or modify existing ones

## Deployment

### Static Hosting

The built app can be deployed to any static hosting service:

- **Netlify**: Drag and drop the `build` folder
- **Vercel**: Connect your GitHub repository
- **GitHub Pages**: Use the `gh-pages` package
- **AWS S3**: Upload the `build` folder contents

### Environment Variables

For production deployment, you can set:

- `REACT_APP_API_URL`: API endpoint for dynamic data loading
- `REACT_APP_DATA_URL`: URL for the publications JSON file

## Troubleshooting

### Common Issues

1. **Data not loading**: Ensure the JSON file is in the `public` folder
2. **Build errors**: Check that all dependencies are installed
3. **Styling issues**: Clear browser cache and restart the dev server

### Getting Help

- Check the browser console for error messages
- Ensure all dependencies are up to date
- Verify the JSON data format matches the expected structure

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the NASA Hackathon and follows the same license terms.
