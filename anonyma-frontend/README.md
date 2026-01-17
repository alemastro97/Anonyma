# Anonyma Frontend

Modern React + TypeScript frontend for the Anonyma API.

## 🌟 Features

- 📝 **Text Anonymization** - Anonymize text in real-time
- 📄 **Document Processing** - Upload and anonymize documents (PDF, Word, Excel, PowerPoint, Images, Email)
- ⚙️ **Settings** - Configure API connection and view system status
- 🎨 **Beautiful UI** - Built with Tailwind CSS
- 🔐 **Enterprise Ready** - Support for API key authentication and rate limiting
- 📊 **Real-time Status** - Live job status updates with progress tracking

## 🚀 Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` if needed:
```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_KEY=your_api_key_here  # Optional
```

### 3. Start Development Server

```bash
npm start
```

Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

## 📦 Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first styling
- **Axios** - HTTP client
- **React Router** - SPA routing

## 📖 Available Scripts

### `npm start`

Runs the app in development mode at [http://localhost:3000](http://localhost:3000).

### `npm test`

Launches the test runner in interactive watch mode.

### `npm run build`

Builds the app for production to the `build` folder.

## 🎯 Features

### Text Anonymization

- Real-time text anonymization with multiple modes
- Detection statistics and confidence scores
- Copy anonymized text
- Example texts for quick testing

### Document Processing

- Drag-and-drop file upload
- Real-time progress tracking
- Download anonymized documents
- Support for 7+ document formats

### Settings

- API health monitoring
- Enterprise features status
- Connection testing
- Persistent configuration

## 🔧 Configuration

Configure the API connection in the **Settings** page or via environment variables.

Settings are stored in `localStorage` and persist across sessions.

## 📁 Project Structure

```
src/
├── components/     # Reusable components
├── pages/          # Page components
├── services/       # API client
├── types/          # TypeScript types
└── App.tsx         # Main app
```

## 🚀 Building for Production

```bash
npm run build
```

Deploy the `build` folder to any static hosting service.

## 📚 Documentation

See the main [Anonyma README](../README.md) for complete project documentation.

---

**Version**: 1.0.0
**Built with**: React + TypeScript + Tailwind CSS
