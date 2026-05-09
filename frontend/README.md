# IoT Blockchain Security - Frontend

A modern, responsive web interface for the IoT Blockchain Security System API.

## Features

- **Dashboard**: Real-time system health and statistics
- **Register Data**: Register IoT sensor data on blockchain with custom fields
- **Verify Data**: Verify data integrity against blockchain records
- **Hash Generator**: Generate SHA-256 hashes for any data
- **Audit Reports**: View system audit logs
- **Statistics**: Monitor system performance and blockchain activity
- **Settings**: Configure API connection parameters

## Getting Started

### Prerequisites
- A modern web browser (Chrome, Firefox, Safari, Edge)
- The API server running on localhost:5000 (or configured via settings)

### Installation

1. Open the frontend in your browser:
   ```
   Open `index.html` directly in your browser
   ```

   Or serve it via HTTP server:
   ```bash
   # Using Python 3
   python -m http.server 8000
   
   # Using Python 2
   python -m SimpleHTTPServer 8000
   
   # Using Node.js (if http-server installed)
   http-server
   ```

2. Access the frontend:
   - If serving via HTTP server: `http://localhost:8000`
   - If opened directly: Use file:/// protocol

3. Configure API settings (if needed):
   - Click the "Settings" icon in the top right
   - Update the API Host and Port (default: localhost:5000)
   - Click "Save Settings"

## Usage

### Dashboard
- View real-time system health
- Monitor blockchain records and account balance
- Check network connectivity status
- Quick access to main features

### Register Data
1. Enter Device ID (e.g., DEVICE_001)
2. Select Sensor Type or keep Custom
3. Enter sensor readings
4. (Optional) Add custom fields using "Add Custom Field"
5. Click "Register on Blockchain"
6. View transaction details upon success

### Verify Data
1. Enter sensor data as JSON format
2. Click "Compute Hash" to calculate data hash
3. Click "Verify Integrity" to check against blockchain
4. View verification results

### Hash Generator
1. Enter any data in JSON format
2. Click "Generate Hash"
3. View SHA-256 hash and copy to clipboard

### Audit Report
- View comprehensive system audit logs
- Check all registered transactions
- Monitor system activities

### Statistics
- Total blockchain records
- Processed records count
- Account balance
- Contract and network information

## API Endpoints

The frontend communicates with these API endpoints:

- `GET /` - API documentation
- `GET /api/docs` - Full API documentation
- `GET /api/health` - System health check
- `POST /api/register` - Register data on blockchain
- `POST /api/verify` - Verify data integrity
- `POST /api/hash` - Generate SHA-256 hash
- `GET /api/audit` - Get audit report
- `GET /api/records` - Get total blockchain records
- `GET /api/stats` - Get system statistics

## Configuration

Settings are stored in browser local storage:
- **apiHost**: API server hostname (default: http://localhost)
- **apiPort**: API server port (default: 5000)

## Features in Detail

### Smart Sensor Selection
Pre-configured fields for common sensor types:
- Temperature (°C)
- Humidity (%)
- Pressure (hPa)
- Motion (detected/true/false)
- GPS (coordinates)

### Custom Fields
Add unlimited custom fields to sensor data for flexibility

### Hash Management
- Automatic hash computation for all data
- Copy hash to clipboard with one click
- SHA-256 algorithm verification

### Real-time Updates
Dashboard automatically refreshes blockchain status every 30 seconds

### Error Handling
Comprehensive error messages and validation feedback

## Troubleshooting

### API Connection Issues
1. Ensure the API server is running on the configured host and port
2. Check browser console for detailed error messages
3. Verify CORS is enabled on the API server
4. Try updating settings and refreshing the page

### JSON Format Errors
- Ensure all JSON is properly formatted
- Use double quotes for JSON keys and string values
- Verify data types (numbers shouldn't be quoted)

### Hash Mismatch
- Ensure the exact same data is being hashed
- Check for trailing whitespace or formatting differences
- Verify the data hasn't been modified

## Browser Support

- Chrome/Chromium 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Files

- `index.html` - Main HTML structure and UI
- `styles.css` - Responsive styling and themes
- `app.js` - API client and business logic

## Security Notes

- All API calls use standard HTTP (configure HTTPS in production)
- No sensitive data is stored in browser local storage (only settings)
- CORS requests require API server to have CORS enabled
- Hash values are computed server-side for security

## Development

To modify the frontend:

1. Edit `index.html` for UI structure
2. Modify `styles.css` for appearance
3. Update `app.js` for functionality
4. Test in browser dev tools (F12)

## License

Part of the IoT Blockchain Security System project.

## Support

For issues or questions:
1. Check the API server logs
2. Review browser console (F12)
3. Verify API endpoints using `/api/docs`
4. Check network tab for failed requests
