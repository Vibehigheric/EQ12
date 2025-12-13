package com.eq12.automation;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import static org.junit.jupiter.api.Assertions.*;

/**
 * Test class for EQ12JavaIntegration
 */
class EQ12JavaIntegrationTest {
    
    @Test
    @DisplayName("Should demonstrate Java 17 features")
    void shouldDemonstrateJava17Features() {
        EQ12JavaIntegration app = new EQ12JavaIntegration();
        
        // This should not throw any exceptions
        assertDoesNotThrow(() -> app.demonstrateJava17Features());
    }
    
    @Test
    @DisplayName("Should create valid EQ12Config record")
    void shouldCreateValidEQ12Config() {
        EQ12JavaIntegration.EQ12Config config = 
            new EQ12JavaIntegration.EQ12Config("EQ12", "1.0.0", true);
        
        assertEquals("EQ12", config.name());
        assertEquals("1.0.0", config.version());
        assertTrue(config.enabled());
    }
    
    @Test
    @DisplayName("Should reject invalid config")
    void shouldRejectInvalidConfig() {
        assertThrows(IllegalArgumentException.class, () -> 
            new EQ12JavaIntegration.EQ12Config("", "1.0.0", true));
        
        assertThrows(IllegalArgumentException.class, () -> 
            new EQ12JavaIntegration.EQ12Config(null, "1.0.0", true));
    }
}
