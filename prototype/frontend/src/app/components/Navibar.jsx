import Link from "next/link";
export default function NavBar() {
    return (
        <nav className="bg-blue-600 p-4 shadow-md">
            <ul className="flex space-x-6 justify-center text-white">
                <li>
                    <Link href="/" className="font-semibold hover:text-yellow-300 transition">Home</Link>
                </li>
                <li>
                    <Link href="/project" className="font-semibold hover:text-yellow-300 transition">Projects</Link>
                </li>
                <li>
                    <Link href="/equipment" className="font-semibold hover:text-yellow-300 transition">Equipments</Link>
                </li>
                <li>
                    <Link href="/yard_data" className="font-semibold hover:text-yellow-300 transition">Yard Data</Link>
                </li>
				<li>
					<Link href="/simulation" className="font-semibold hover:text-yellow-300 transition">Simulation</Link>	
				</li>
            </ul>
        </nav>
    );
}
