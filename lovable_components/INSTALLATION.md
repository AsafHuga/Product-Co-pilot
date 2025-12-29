# Installing Product Metrics Copilot in Lovable

## Step 1: Copy the Component

1. Create a new file in your Lovable project: `src/components/MetricsAnalyzer.tsx`
2. Copy the entire contents of `MetricsAnalyzer.tsx` into that file

## Step 2: Install Dependencies

Lovable should already have these, but make sure you have:
- `react`
- `lucide-react` (for icons)

If you need to add lucide-react, Lovable usually auto-installs when you use the component.

## Step 3: Add to Your Page

In your Lovable page or app component:

```tsx
import MetricsAnalyzer from '@/components/MetricsAnalyzer';

export default function App() {
  return <MetricsAnalyzer />;
}
```

## Step 4: Configure API URL

In `MetricsAnalyzer.tsx`, update the API_URL:

```typescript
// For local development
const API_URL = 'http://localhost:8000';

// For production (after deploying your API)
const API_URL = 'https://your-api-domain.com';
```

## Step 5: Handle CORS (if needed)

If you get CORS errors, make sure your API has CORS enabled (already configured in `api.py`).

For production, update the CORS settings in `metrics_copilot/api.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-lovable-app.lovable.app"],  # Your Lovable domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Step 6: Test It!

1. Make sure your API is running: `./test_api.sh`
2. Open your Lovable app
3. Upload a CSV file from the `examples/` folder
4. Click "Analyze Metrics"
5. See the magic happen! ✨

---

## Alternative: Simple Integration (Just the Upload)

If you want to start simpler, here's a minimal component:

```tsx
import { useState } from 'react';

export default function SimpleMetricsUpload() {
  const [results, setResults] = useState(null);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch('http://localhost:8000/analyze/quick', {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();
    setResults(data);
  };

  return (
    <div className="p-8">
      <input type="file" accept=".csv" onChange={handleUpload} />
      {results && <pre>{JSON.stringify(results, null, 2)}</pre>}
    </div>
  );
}
```

---

## Troubleshooting

### "Failed to fetch" error
- Make sure the API server is running (`./test_api.sh`)
- Check the API URL matches where your server is running
- Check browser console for CORS errors

### "Analysis failed" error
- Check that you're uploading a CSV file
- Look at the API server logs for details
- Try with one of the sample files first

### Component not showing
- Make sure you imported it correctly
- Check that lucide-react is installed
- Look for TypeScript errors in Lovable

---

## Next Steps

1. **Customize the UI** - Modify colors, layout, add your branding
2. **Add Features** - File history, saved analyses, export to PDF
3. **Deploy API** - Use Railway, Render, or Vercel
4. **Production Ready** - Add authentication, rate limiting, error tracking

---

## Example: Adding to Lovable Dashboard

```tsx
import MetricsAnalyzer from '@/components/MetricsAnalyzer';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

export default function Dashboard() {
  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Analytics Dashboard</h1>

      <Tabs defaultValue="metrics">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="metrics">Metrics Copilot</TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          {/* Your existing dashboard */}
        </TabsContent>

        <TabsContent value="metrics">
          <MetricsAnalyzer />
        </TabsContent>
      </Tabs>
    </div>
  );
}
```

Happy analyzing! 🚀
