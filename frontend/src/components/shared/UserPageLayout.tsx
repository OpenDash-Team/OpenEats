import { type ReactNode } from 'react'
import MyNavBar from './MyNavBar';

interface UserPageLayoutProps {
    className?: string;
    children?: ReactNode;
}

const UserPageLayout = (props: UserPageLayoutProps) => {
  return (
    <div data-bs-theme="dark">
        <MyNavBar />
        
        <div className={"min-vh-100 bg-dark text-body py-4 d-flex flex-column " + (props.className ?? "")} style={{paddingInline: "8rem"}}>
            {props.children}
        </div>
    </div>
  )
}

export default UserPageLayout