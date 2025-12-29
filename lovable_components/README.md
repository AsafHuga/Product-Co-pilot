# Lovable Components for Product Metrics Copilot

This folder contains everything you need to integrate the Product Metrics Copilot into your Lovable application.

## 📁 Files

- **MetricsAnalyzer.tsx** - Complete React/TypeScript component (copy-paste ready)
- **QUICK_START.md** - Get started in 3 steps
- **INSTALLATION.md** - Detailed installation guide
- **README.md** - This file

## ⚡ Quick Start

1. Copy `MetricsAnalyzer.tsx` to your Lovable project
2. Import and use: `<MetricsAnalyzer />`
3. Upload a CSV and analyze!

See [QUICK_START.md](QUICK_START.md) for details.

## 🎨 What's Included

The component is a complete, production-ready React component with:

✅ **TypeScript** - Fully typed with interfaces
✅ **Tailwind CSS** - Beautiful, responsive design
✅ **Lucide Icons** - Professional icon set
✅ **Error Handling** - User-friendly error messages
✅ **Loading States** - Animated spinners
✅ **Responsive** - Works on mobile and desktop

## 📊 Features

- File upload with validation
- Executive summary dashboard
- KPI detection and display
- Trend analysis with indicators
- Change point visualization
- AI-generated hypotheses
- Decision recommendations

## 🔧 Requirements

- React 18+
- TypeScript
- Tailwind CSS
- lucide-react (for icons)
- API server running (see ../test_api.sh)

## 🚀 Usage

```tsx
import MetricsAnalyzer from './components/MetricsAnalyzer';

function App() {
  return (
    <div>
      <MetricsAnalyzer />
    </div>
  );
}
```

## 🎯 API Configuration

Update the API_URL in MetricsAnalyzer.tsx:

```typescript
// Local development
const API_URL = 'http://localhost:8000';

// Production
const API_URL = 'https://your-api-domain.com';
```

## 📖 Documentation

- [Quick Start Guide](QUICK_START.md) - 3-step setup
- [Installation Guide](INSTALLATION.md) - Detailed instructions
- [Full Integration Docs](../LOVABLE_INTEGRATION.md) - Complete API docs

## 🧪 Testing

Test with the sample files in `../examples/`:
- sample_timeseries.csv
- sample_experiment.csv
- sample_messy.csv

## 💡 Customization

The component is designed to be easily customizable:

- Change colors by updating Tailwind classes
- Modify layout in the JSX
- Add/remove sections as needed
- Integrate with your existing design system

## 🆘 Support

Having issues? Check:
1. API server is running: `../test_api.sh`
2. API_URL is correct
3. CORS is enabled (already configured)
4. Browser console for errors

## 📝 License

MIT - Same as the main Product Metrics Copilot project

---

Made with ❤️ for Product Managers
