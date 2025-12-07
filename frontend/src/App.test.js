import { render, screen } from '@testing-library/react';
import App from './App';

test('renders login screen', () => {
  render(<App />);
  
  // This looks for the "Login" text which should be visible when the app starts
  // If your App.js says "Customer Portal Login", this will find it.
  const loginHeader = screen.getByText(/Login/i);
  
  expect(loginHeader).toBeInTheDocument();
});