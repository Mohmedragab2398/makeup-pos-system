import React from 'react';
import { Box, Typography, Paper, Stack } from '@mui/material';

const StreamlitPOSPreview: React.FC = () => {
  return (
    <Box sx={{ p: 3, maxWidth: 1200, mx: 'auto' }}>
      <Paper elevation={2} sx={{ p: 4, mb: 3, textAlign: 'center' }}>
        <Stack spacing={2} alignItems="center">
          {/* Logo placeholder */}
          <Box
            sx={{
              width: 200,
              height: 200,
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #008080, #20b2aa)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontSize: '3rem',
              fontWeight: 'bold',
              mb: 2
            }}
          >
            YS
          </Box>
          
          <Typography variant="h3" component="h1" sx={{ fontWeight: 'bold', color: '#008080' }}>
            Yalla Shopping
          </Typography>
          
          <Typography variant="h6" sx={{ color: '#666' }}>
            Py Saso Mostafa
          </Typography>
          
          <Typography variant="body2" sx={{ color: '#999' }}>
            Designed by Mohamed Ragab
          </Typography>
        </Stack>
      </Paper>

      <Paper elevation={1} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" gutterBottom sx={{ color: '#008080', fontWeight: 'bold' }}>
          🛒 Yalla Shopping POS System
        </Typography>
        
        <Typography variant="body1" paragraph>
          واجهة تعمل من اللابتوب والموبايل. قاعدة بيانات: Google Sheets.
        </Typography>

        <Stack spacing={2}>
          <Box sx={{ p: 2, bgcolor: '#f0f8ff', borderRadius: 2 }}>
            <Typography variant="h6" gutterBottom>Features Updated:</Typography>
            <ul>
              <li>✅ New Yalla Shopping logo integration</li>
              <li>✅ Updated branding with "Py Saso Mostafa"</li>
              <li>✅ Enhanced invoice design with logo</li>
              <li>✅ Professional logo display throughout app</li>
              <li>✅ Automatic logo detection system</li>
              <li>✅ Fallback logo system for reliability</li>
            </ul>
          </Box>

          <Box sx={{ p: 2, bgcolor: '#fff8dc', borderRadius: 2 }}>
            <Typography variant="h6" gutterBottom>App Sections:</Typography>
            <Stack direction="row" spacing={2} flexWrap="wrap">
              {[
                '📊 لوحة المعلومات',
                '🧾 بيع جديد (POS)',
                '📦 المنتجات',
                '👤 العملاء',
                '📥 حركة المخزون',
                '📈 التقارير',
                '⚙️ الإعدادات'
              ].map((section, index) => (
                <Paper key={index} sx={{ p: 1, bgcolor: 'white', fontSize: '0.9rem' }}>
                  {section}
                </Paper>
              ))}
            </Stack>
          </Box>

          <Box sx={{ p: 2, bgcolor: '#f0fff0', borderRadius: 2 }}>
            <Typography variant="h6" gutterBottom>Logo Integration:</Typography>
            <Typography variant="body2">
              The new circular teal logo with woman silhouette and decorative leaves has been integrated into:
            </Typography>
            <ul>
              <li>Main app header display</li>
              <li>Customer invoice generation</li>
              <li>Settings page management</li>
              <li>Professional branding throughout</li>
            </ul>
          </Box>
        </Stack>
      </Paper>

      <Paper elevation={1} sx={{ p: 3, textAlign: 'center', bgcolor: '#008080', color: 'white' }}>
        <Typography variant="h6">
          Streamlit POS System - Ready for Deployment
        </Typography>
        <Typography variant="body2" sx={{ mt: 1, opacity: 0.9 }}>
          Save logo as assets/logo_yalla_shopping.png to activate new branding
        </Typography>
      </Paper>
    </Box>
  );
};

export default StreamlitPOSPreview;