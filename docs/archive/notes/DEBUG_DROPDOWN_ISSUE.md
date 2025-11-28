# Debug Dropdown Pre-population Issue - User Testing Guide

## Issue Description
User reports: "still problems when doing changes to both a bow and equipment. The dropdowns when you edit don't have the last value set when editing."

## Enhanced Debugging Setup

I've added comprehensive console logging to `CustomEquipmentForm.vue` that will help us identify exactly what's happening during the equipment editing process.

## Testing Steps

### 1. Open Browser Developer Tools
- Open Chrome/Firefox Developer Tools (F12)
- Go to the Console tab
- Clear the console for clean output

### 2. Navigate to Equipment Editing
1. Go to http://localhost:3000
2. Login to your account
3. Navigate to a bow setup that has equipment
4. Go to Equipment tab
5. Click the edit button (pencil icon) on any equipment item

### 3. Monitor Console Output

When you click edit, you should see detailed debug output with `🔧` prefixes. Look for these key logs:

**A. Initial Equipment Data:**
```
🔧 DROPDOWN DEBUG: initializeForEditing called
🔧 Equipment prop received: { ... full equipment object ... }
🔧 Available equipment fields: ["id", "manufacturer_name", ...]
```

**B. Form Schema Loading:**
```
🔧 DROPDOWN DEBUG: loadFormSchema called for category: [category]
🔧 Current editing mode: true
🔧 Form schema loaded: [number] fields
```

**C. Specifications Processing:**
```
🔧 DROPDOWN DEBUG: initializeEditingSpecifications called
🔧 Initial equipment object: { ... }
🔧 Equipment specifications field: { ... }
🔧 Using specifications from field: [specifications or custom_specifications]
🔧 Parsed specifications: { ... }
```

**D. Field Processing:**
```
🔧 Processing field: sight_type (dropdown)
🔧 Dropdown field sight_type value: "scope"
🔧 Dropdown field sight_type options: ["single-pin", "multi-pin", "scope"]
```

### 4. What to Look For

**✅ Expected Behavior:**
- Equipment object should contain a `specifications` field with your saved values
- Field processing should show the correct values for each dropdown
- Final form specifications should match your saved data

**❌ Problem Indicators:**
- Equipment object missing `specifications` field
- `specifications` field is empty `{}`
- Field values are not being applied to form
- Specifications being reset during schema loading

### 5. Copy and Send Debug Output

Please copy the complete console output and send it to me. This will help identify:

1. **Data Structure Issues**: Is the API returning specifications in the expected format?
2. **Field Name Mismatches**: Are we looking for specs in the right field?
3. **Timing Issues**: Is the form schema loading before or after specifications are set?
4. **Value Conversion Problems**: Are dropdown values being processed correctly?

## Expected Data Flow

Here's what should happen when editing equipment:

1. **BowEquipmentManager** passes `initialEquipment` prop to `CustomEquipmentForm`
2. **initializeForEditing()** sets basic form fields (manufacturer, model, category)  
3. **loadFormSchema()** loads field definitions for the equipment category
4. **initializeEditingSpecifications()** processes specifications and applies them to form fields
5. **Form renders** with pre-populated dropdown values

## Common Issues to Check

### Issue 1: API Response Format
Check if the equipment object contains:
```javascript
{
  "specifications": {
    "sight_type": "scope",
    "adjustment_type": "micro"
  }
}
```

### Issue 2: Field Name Mismatch
The form might be looking for `specifications` but API returns `custom_specifications`

### Issue 3: Timing Race Condition
Schema loading might reset specifications after they're set

### Issue 4: Value Format Issues
Multi-select fields might need array conversion, dropdowns might have string/option mismatches

## Next Steps

After you provide the console output, I can:

1. **Identify the root cause** from the debug data
2. **Implement the specific fix** needed
3. **Remove the debug logging** once issue is resolved
4. **Create proper tests** to prevent regression

## Remove Debug Logging

Once we solve the issue, I'll remove all the console.log statements to clean up the code.

---

**Please run through these steps and provide the console output - this will help us solve the dropdown pre-population issue quickly and definitively.**