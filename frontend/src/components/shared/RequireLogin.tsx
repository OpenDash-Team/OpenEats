import { Navigate, Outlet } from 'react-router-dom'
import useLoggedIn from '../../hooks/useLoggedIn'

const RequireLogin = () => {
    const loginStatus = useLoggedIn();

    if (loginStatus === 'checking') return <p>Loading...</p>;
    if (loginStatus === 'error') return <p role="alert">Could not check your session. Please try again.</p>;
    if (loginStatus === 'loggedOut') return <Navigate to="/login" replace />;

    return <Outlet />;
}

export default RequireLogin
