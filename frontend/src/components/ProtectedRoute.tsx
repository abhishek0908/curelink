import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export const ProtectedRoute = () => {
    const { user, isLoading } = useAuth();

    if (isLoading) {
        return <div className="flex items-center justify-center h-screen">Loading...</div>;
    }

    if (!user) {
        return <Navigate to="/login" replace />;
    }

    return <Outlet />;
};

export const OnboardingRoute = () => {
    const { user, isLoading } = useAuth();

    if (isLoading) return <div>Loading...</div>;

    if (!user) return <Navigate to="/login" replace />;

    // If user has completed onboarding, redirect to dashboard (or wherever)
    // But strictly speaking, we might want to allow them to edit it.
    // For now, let's just protect it with auth.

    return <Outlet />;
}
