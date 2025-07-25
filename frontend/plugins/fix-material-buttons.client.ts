export default defineNuxtPlugin(() => {
  // Simple CSS-only approach to avoid hydration issues
  if (process.client) {
    // Add CSS styles after hydration is complete
    const addButtonStyles = () => {
      // Check if our custom styles are already added
      if (document.getElementById('custom-button-fix')) {
        return;
      }
      
      const style = document.createElement('style');
      style.id = 'custom-button-fix';
      style.textContent = `
        /* Post-hydration button fixes */
        md-filled-button {
          background: #f3f4f6 !important;
          color: #000000 !important;
          border: none !important;
          border-radius: 8px !important;
          padding: 8px 16px !important;
          font-size: 14px !important;
          font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
          font-weight: 500 !important;
          min-height: 40px !important;
          display: inline-flex !important;
          align-items: center !important;
          justify-content: center !important;
          cursor: pointer !important;
          text-decoration: none !important;
        }
        
        md-filled-button * {
          color: #000000 !important;
          font-size: 14px !important;
          opacity: 1 !important;
          visibility: visible !important;
        }
        
        md-filled-button i {
          margin-right: 6px !important;
          font-size: 14px !important;
          color: #000000 !important;
        }
        
        /* Dark mode */
        .dark md-filled-button {
          background: #4b5563 !important;
          color: #f9fafb !important;
        }
        
        .dark md-filled-button *,
        .dark md-filled-button i {
          color: #f9fafb !important;
        }
      `;
      
      document.head.appendChild(style);
    };
    
    // Wait for hydration to complete
    nextTick(() => {
      setTimeout(addButtonStyles, 100);
    });
  }
});