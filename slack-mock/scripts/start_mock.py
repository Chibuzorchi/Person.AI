#!/usr/bin/env python3
"""
Start Slack Mock Server - Main entry point
"""
import asyncio
import argparse
import logging
from slack_mock_server import SlackMockServer

def setup_logging(level=logging.INFO):
    """Setup logging configuration"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('slack_mock.log')
        ]
    )

async def main():
    """Main function to start the mock server"""
    parser = argparse.ArgumentParser(description='Start Slack Mock Server')
    parser.add_argument('--wiremock-url', default='http://localhost:8080', 
                       help='WireMock server URL')
    parser.add_argument('--websocket-port', type=int, default=8765,
                       help='WebSocket server port')
    parser.add_argument('--log-level', default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(getattr(logging, args.log_level))
    logger = logging.getLogger(__name__)
    
    # Create and start server
    server = SlackMockServer(
        wiremock_url=args.wiremock_url,
        websocket_port=args.websocket_port
    )
    
    logger.info(f"Starting Slack Mock Server...")
    logger.info(f"WireMock URL: {args.wiremock_url}")
    logger.info(f"WebSocket Port: {args.websocket_port}")
    
    try:
        await server.start_websocket_server()
    except KeyboardInterrupt:
        logger.info("Shutting down Slack Mock Server...")
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
