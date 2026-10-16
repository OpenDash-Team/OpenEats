import { type ReactNode } from 'react'
import MyNavBar from './MyNavBar';

interface CustomerPageLayoutProps {
    className?: string;
    children?: ReactNode;
}

const CustomerPageLayout = (props: CustomerPageLayoutProps) => {
  return (
    <div data-bs-theme="dark">
        <MyNavBar />
        
        <div className={"min-vh-100 bg-dark text-white py-4 d-flex flex-column " + (props.className ?? "")} style={{paddingInline: "8rem"}}>
            {props.children}
        </div>
    </div>
  )
}

export default CustomerPageLayout