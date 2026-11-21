import { useEffect, useState } from 'react'
import { fetchCustomer } from '../api/fetchCustomer'

const useLoggedIn = () => {
    const [status, setStatus] = useState<'checking' | 'loggedIn' | 'loggedOut' | 'error'>(
        localStorage.getItem('token') ? 'checking' : 'loggedOut'
    );

    useEffect(() => {
        let active = true;
        const onSessionExpired = () => setStatus('loggedOut');
        const onStorage = (event: StorageEvent) => {
            if (event.key === 'token' && !event.newValue) setStatus('loggedOut');
        }
        window.addEventListener('session-expired', onSessionExpired);
        window.addEventListener('storage', onStorage);

        if (localStorage.getItem('token')) {
            fetchCustomer().then((customer) => {
                if (!active || !localStorage.getItem('token')) return;
                localStorage.setItem('userMode', customer.role === 'owner' ? 'restaurant' : 'customer');
                setStatus('loggedIn');
            }).catch(() => {
                if (active) setStatus(localStorage.getItem('token') ? 'error' : 'loggedOut');
            });
        }

        return () => {
            active = false;
            window.removeEventListener('session-expired', onSessionExpired);
            window.removeEventListener('storage', onStorage);
        };
    }, []);

    return status;
}

export default useLoggedIn
