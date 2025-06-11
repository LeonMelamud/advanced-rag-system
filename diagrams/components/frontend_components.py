#!/usr/bin/env python3
"""
Advanced RAG System - Frontend Components
Shows React application structure and component hierarchy
"""

from pathlib import Path

from diagrams import Cluster, Diagram, Edge
from diagrams.generic.compute import Rack
from diagrams.onprem.client import User
from diagrams.onprem.network import Nginx
from diagrams.programming.framework import React
from diagrams.programming.language import JavaScript, TypeScript

# Frontend colors
COLORS = {
    "user_interaction": "#3498db",  # Blue
    "components": "#2ecc71",  # Green
    "state": "#9b59b6",  # Purple
    "api": "#e74c3c",  # Red
    "routing": "#f39c12",  # Orange
    "utilities": "#1abc9c",  # Teal
}

with Diagram(
    "Advanced RAG System - Frontend Components",
    filename=str(Path(__file__).parent.parent / "generated" / "frontend_components"),
    show=False,
    direction="TB",
    graph_attr={"fontsize": "18", "bgcolor": "white"},
):

    # User
    user = User("User")

    # Main App Structure
    with Cluster("React Application (TypeScript)"):
        # App Root
        app_root = React("App.tsx\n(Root Component)")

        # Routing Layer
        with Cluster("Routing Layer"):
            router = TypeScript("React Router\n(Navigation)")
            route_guard = TypeScript("Route Guard\n(Auth Protection)")

        # Layout Components
        with Cluster("Layout Components"):
            header = React("Header\n(Navigation, User Menu)")
            sidebar = React("Sidebar\n(Collections, Navigation)")
            main_layout = React("MainLayout\n(Page Container)")
            footer = React("Footer\n(Links, Info)")

        # Page Components
        with Cluster("Page Components"):
            # Auth Pages
            with Cluster("Auth Pages"):
                login_page = React("LoginPage\n(/login)")
                register_page = React("RegisterPage\n(/register)")
                profile_page = React("ProfilePage\n(/profile)")

            # Core Pages
            with Cluster("Core Pages"):
                dashboard_page = React("DashboardPage\n(/dashboard)")
                collections_page = React("CollectionsPage\n(/collections)")
                chat_page = React("ChatPage\n(/chat)")
                search_page = React("SearchPage\n(/search)")
                upload_page = React("UploadPage\n(/upload)")

        # Feature Components
        with Cluster("Feature Components"):
            # Collection Components
            with Cluster("Collection Components"):
                collection_list = React("CollectionList\n(Grid/List View)")
                collection_card = React("CollectionCard\n(Preview)")
                collection_form = React("CollectionForm\n(Create/Edit)")
                collection_settings = React("CollectionSettings\n(Permissions)")

            # Document Components
            with Cluster("Document Components"):
                document_list = React("DocumentList\n(File List)")
                document_upload = React("DocumentUpload\n(Drag & Drop)")
                document_preview = React("DocumentPreview\n(Content View)")
                document_status = React("DocumentStatus\n(Processing)")

            # Chat Components
            with Cluster("Chat Components"):
                chat_interface = React("ChatInterface\n(Main Chat)")
                message_list = React("MessageList\n(Conversation)")
                message_input = React("MessageInput\n(Query Input)")
                source_display = React("SourceDisplay\n(Citations)")

            # Search Components
            with Cluster("Search Components"):
                search_bar = React("SearchBar\n(Query Input)")
                search_filters = React("SearchFilters\n(Collection, Type)")
                search_results = React("SearchResults\n(Result List)")
                result_card = React("ResultCard\n(Individual Result)")

        # UI Components Library
        with Cluster("UI Components Library"):
            # Base Components
            with Cluster("Base Components"):
                button = React("Button\n(Primary, Secondary)")
                input = React("Input\n(Text, Search)")
                modal = React("Modal\n(Dialogs)")
                loading = React("Loading\n(Spinners, Skeletons)")

            # Form Components
            with Cluster("Form Components"):
                form_wrapper = React("FormWrapper\n(Validation)")
                file_input = React("FileInput\n(Upload)")
                select = React("Select\n(Dropdown)")
                checkbox = React("Checkbox\n(Multi-select)")

            # Display Components
            with Cluster("Display Components"):
                card = React("Card\n(Content Container)")
                table = React("Table\n(Data Display)")
                pagination = React("Pagination\n(Page Navigation)")
                toast = React("Toast\n(Notifications)")

    # State Management
    with Cluster("State Management"):
        # Global State
        with Cluster("Global State (Zustand/Redux)"):
            auth_store = TypeScript("AuthStore\n(User, Tokens)")
            collection_store = TypeScript("CollectionStore\n(Collections)")
            chat_store = TypeScript("ChatStore\n(Conversations)")
            ui_store = TypeScript("UIStore\n(Theme, Modals)")

        # Local State
        with Cluster("Local State (React Hooks)"):
            use_auth = TypeScript("useAuth\n(Authentication)")
            use_api = TypeScript("useAPI\n(HTTP Requests)")
            use_upload = TypeScript("useUpload\n(File Upload)")
            use_search = TypeScript("useSearch\n(Search Logic)")

    # API Integration
    with Cluster("API Integration"):
        # HTTP Client
        api_client = TypeScript("API Client\n(Axios/Fetch)")

        # API Services
        with Cluster("API Services"):
            auth_api = TypeScript("AuthAPI\n(/auth/*)")
            collection_api = TypeScript("CollectionAPI\n(/collections/*)")
            file_api = TypeScript("FileAPI\n(/files/*)")
            chat_api = TypeScript("ChatAPI\n(/chat/*)")

        # API Utilities
        with Cluster("API Utilities"):
            interceptors = TypeScript("Interceptors\n(Auth, Errors)")
            cache_manager = TypeScript("CacheManager\n(React Query)")
            error_handler = TypeScript("ErrorHandler\n(Global Errors)")

    # Utilities & Helpers
    with Cluster("Utilities & Helpers"):
        # Core Utilities
        with Cluster("Core Utilities"):
            validators = TypeScript("Validators\n(Form Validation)")
            formatters = TypeScript("Formatters\n(Date, Text)")
            constants = TypeScript("Constants\n(Config, Enums)")
            helpers = TypeScript("Helpers\n(Common Functions)")

        # Styling
        with Cluster("Styling"):
            tailwind = Rack("Tailwind CSS\n(Utility Classes)")
            theme = TypeScript("Theme\n(Colors, Spacing)")
            responsive = TypeScript("Responsive\n(Breakpoints)")

    # External Services
    backend_api = Nginx("Backend API\n(FastAPI)")

    # User Interaction Flow
    user >> Edge(color=COLORS["user_interaction"]) >> app_root

    # App Structure Flow
    app_root >> Edge(color=COLORS["routing"]) >> router
    router >> Edge(color=COLORS["routing"]) >> route_guard
    route_guard >> Edge(color=COLORS["components"]) >> main_layout

    # Layout Flow
    main_layout >> Edge(color=COLORS["components"]) >> [header, sidebar, footer]
    (
        main_layout
        >> Edge(color=COLORS["components"])
        >> [dashboard_page, collections_page, chat_page, search_page, upload_page]
    )

    # Page to Feature Components
    collections_page >> Edge(color=COLORS["components"]) >> [collection_list, collection_form]
    collection_list >> Edge(color=COLORS["components"]) >> collection_card

    upload_page >> Edge(color=COLORS["components"]) >> [document_upload, document_status]
    document_upload >> Edge(color=COLORS["components"]) >> [file_input, loading]

    chat_page >> Edge(color=COLORS["components"]) >> chat_interface
    (
        chat_interface
        >> Edge(color=COLORS["components"])
        >> [message_list, message_input, source_display]
    )

    search_page >> Edge(color=COLORS["components"]) >> [search_bar, search_filters, search_results]
    search_results >> Edge(color=COLORS["components"]) >> result_card

    # UI Components Usage (fixed syntax)
    collection_form >> Edge(color=COLORS["components"], style="dashed") >> button
    document_upload >> Edge(color=COLORS["components"], style="dashed") >> button
    message_input >> Edge(color=COLORS["components"], style="dashed") >> input
    search_bar >> Edge(color=COLORS["components"], style="dashed") >> input

    collection_list >> Edge(color=COLORS["components"], style="dashed") >> card
    search_results >> Edge(color=COLORS["components"], style="dashed") >> pagination

    # State Management Connections
    [login_page, profile_page] >> Edge(color=COLORS["state"]) >> auth_store
    [collections_page, collection_form] >> Edge(color=COLORS["state"]) >> collection_store
    [chat_page, chat_interface] >> Edge(color=COLORS["state"]) >> chat_store
    [header, sidebar] >> Edge(color=COLORS["state"]) >> ui_store

    # Hook Usage
    [login_page, header] >> Edge(color=COLORS["state"], style="dashed") >> use_auth
    [collection_form, chat_interface] >> Edge(color=COLORS["state"], style="dashed") >> use_api
    document_upload >> Edge(color=COLORS["state"], style="dashed") >> use_upload
    search_page >> Edge(color=COLORS["state"], style="dashed") >> use_search

    # API Integration Flow
    [use_auth, auth_store] >> Edge(color=COLORS["api"]) >> auth_api
    [collection_store, use_api] >> Edge(color=COLORS["api"]) >> collection_api
    [use_upload, document_upload] >> Edge(color=COLORS["api"]) >> file_api
    [chat_store, use_api] >> Edge(color=COLORS["api"]) >> chat_api

    # API Client Flow
    [auth_api, collection_api, file_api, chat_api] >> Edge(color=COLORS["api"]) >> api_client
    api_client >> Edge(color=COLORS["api"]) >> interceptors
    api_client >> Edge(color=COLORS["api"]) >> cache_manager
    api_client >> Edge(color=COLORS["api"]) >> error_handler

    # External API Connection
    api_client >> Edge(color=COLORS["api"], style="bold") >> backend_api

    # Utilities Usage
    collection_form >> Edge(color=COLORS["utilities"], style="dashed") >> validators
    message_input >> Edge(color=COLORS["utilities"], style="dashed") >> validators
    message_list >> Edge(color=COLORS["utilities"], style="dashed") >> formatters
    search_results >> Edge(color=COLORS["utilities"], style="dashed") >> formatters
    app_root >> Edge(color=COLORS["utilities"], style="dashed") >> constants
    app_root >> Edge(color=COLORS["utilities"], style="dashed") >> theme

    # Styling
    app_root >> Edge(color=COLORS["utilities"], style="dashed") >> tailwind
    main_layout >> Edge(color=COLORS["utilities"], style="dashed") >> responsive

print("✅ Generated: Frontend Components Diagram")
