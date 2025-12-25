/**
 * Type definitions for the Local Voice Assistant Frontend.
 */

/**
 * Health check response from the backend API.
 * Matches the backend HealthResponse Pydantic model.
 */
export interface HealthResponse {
  status: "healthy" | "unhealthy";
  version: string;
  timestamp: string;
}
