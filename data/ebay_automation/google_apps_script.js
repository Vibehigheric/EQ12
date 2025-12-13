
// Google Apps Script for EQ12 eBay Automation
// Paste this into Google Apps Script (script.google.com)

function buildLabelCSV() {
  const ss = SpreadsheetApp.getActive();
  const sheet = ss.getSheetByName("Orders");
  
  if (!sheet) {
    Browser.msgBox("Error", "Orders sheet not found. Please create an Orders sheet first.", Browser.Buttons.OK);
    return;
  }
  
  const rows = sheet.getDataRange().getValues();
  const headers = rows.shift();
  
  // Build CSV data
  const csvData = [];
  csvData.push(["order_id","to_name","address1","city","state","zip","country","weight_oz","box_type","insurance_value"]);
  
  rows.forEach(row => {
    if (row[0]) { // If order ID exists
      const orderData = [
        row[0] || "",  // Order ID
        row[1] || "",  // Name
        row[2] || "",  // Address1
        row[3] || "",  // City
        row[4] || "",  // State
        row[5] || "",  // Zip
        row[6] || "US", // Country
        row[7] || 16,  // Weight (oz)
        row[8] || "medium_box", // Box type
        row[9] || 50   // Insurance value
      ];
      csvData.push(orderData);
    }
  });
  
  // Convert to CSV string
  const csvString = csvData.map(row => 
    row.map(cell => `"${(cell||"").toString().replace(/"/g,'""')}"`).join(",")
  ).join("\n");
  
  // Create file in Google Drive
  const fileName = `EQ12_Labels_${new Date().getTime()}.csv`;
  const blob = Utilities.newBlob(csvString, 'text/csv', fileName);
  const file = DriveApp.createFile(blob);
  
  Browser.msgBox("Success", `CSV created: ${fileName}\nFile ID: ${file.getId()}\nShare this file with your shipping provider.`, Browser.Buttons.OK);
  
  // Log the file URL
  console.log(`CSV file created: ${file.getUrl()}`);
  
  return file.getUrl();
}

function calculateProfitMargins() {
  const ss = SpreadsheetApp.getActive();
  const sheet = ss.getSheetByName("EQ12_eBay_Automation");
  
  if (!sheet) {
    Browser.msgBox("Error", "EQ12_eBay_Automation sheet not found.", Browser.Buttons.OK);
    return;
  }
  
  const range = sheet.getDataRange();
  const values = range.getValues();
  
  // Update profit calculations for each row (starting from row 2)
  for (let i = 1; i < values.length; i++) {
    const row = i + 1;
    
    // Set formulas if they don't exist
    if (!sheet.getRange(`O${row}`).getFormula()) {
      sheet.getRange(`O${row}`).setFormula(`=E${row}+L${row}`); // Gross Revenue
    }
    if (!sheet.getRange(`P${row}`).getFormula()) {
      sheet.getRange(`P${row}`).setFormula(`=E${row}*M${row}+O${row}*N${row}+0.30`); // Total Fees
    }
    if (!sheet.getRange(`Q${row}`).getFormula()) {
      sheet.getRange(`Q${row}`).setFormula(`=O${row}-P${row}-D${row}-T${row}-U${row}`); // Net Profit
    }
    if (!sheet.getRange(`R${row}`).getFormula()) {
      sheet.getRange(`R${row}`).setFormula(`=IF(O${row}>0,Q${row}/O${row}*100,0)`); // Profit Margin %
    }
  }
  
  Browser.msgBox("Success", "Profit margin formulas updated for all rows!", Browser.Buttons.OK);
}

function createMenus() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('EQ12 eBay Tools')
    .addItem('Generate Label CSV', 'buildLabelCSV')
    .addItem('Calculate Profit Margins', 'calculateProfitMargins')
    .addSeparator()
    .addItem('Setup Instructions', 'showSetupInstructions')
    .addToUi();
}

function showSetupInstructions() {
  const instructions = `
EQ12 eBay Automation Setup:

1. Create an "Orders" sheet with columns:
   - Order ID, Name, Address1, City, State, Zip, Country, Weight (oz), Box Type, Insurance Value

2. Use the "EQ12_eBay_Automation" sheet for inventory management

3. Use "Generate Label CSV" to create shipping files

4. Upload CSV to Pirate Ship or EasyPost for bulk label creation

Need help? Contact EQ12 Support.
  `;
  
  Browser.msgBox("Setup Instructions", instructions, Browser.Buttons.OK);
}

function onOpen() {
  createMenus();
}
