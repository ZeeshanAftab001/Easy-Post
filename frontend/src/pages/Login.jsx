
import Form from '../components/Form.jsx';

export default function Login({ className }) {
  return (
    <Form route="/api/auth/auth/" method="login" />
  );
}