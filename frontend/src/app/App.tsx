import { RouterProvider } from 'react-router';
import { router } from './routes';
import { LocationProvider } from '../context/LocationContext';

export default function App() {
  return (
    <div className="dark">
      <LocationProvider>
        <RouterProvider router={router} />
      </LocationProvider>
    </div>
  );
}
