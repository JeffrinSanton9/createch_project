import Link from "next/link";
export default function NavBar() {
    return (
        <>
            <Link href="/">Home </Link>
            <Link href="/project">Projects </Link>
            <Link href="/equipment">Equipments </Link>
            <Link href="/yard_data">Yard Data </Link>
        </>
    );
}
