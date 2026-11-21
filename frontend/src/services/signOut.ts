import { logout } from '../api/logout'

export const signOut = async () => {
    try {
        await logout();
    } catch {
        // The local token is cleared even if the request fails.
    }
    localStorage.setItem('userMode', '');
    localStorage.removeItem('restaurantId');
    window.location.replace('/login');
}
